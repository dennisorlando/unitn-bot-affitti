import yaml
import time
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from telethon import TelegramClient

from ai_pipeline import process_message
from db_helpers import db_store_messages_batch, db_get_last_message_id

def init_app():
    app = Flask(__name__)
    CORS(app)

    # Init config
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    app.config["telegram"] = config["telegram"]
    app.config["gemini"] = config["gemini"]
    
    # Init mongodb client
    mdb_client = MongoClient("mongodb://mongodb:27017", 
                             serverSelectionTimeoutMS=3000,
                             socketTimeoutMS=3000,
                             connectTimeoutMS=3000,
                             )
    db = mdb_client["unitn-rents"]
       
    # Get active chats
    @app.route("/active_chats", methods=["GET"])
    def get_active_chats():
        chat_names = list(map(lambda x: x["_id"], db["active_chats"].find({})))
        return jsonify({"chat_names": chat_names})

    # Add active chat
    @app.route("/active_chats", methods=["POST"])
    def add_active_chat():
        data = request.get_json(force=True)
        chat_name = data.get("name")
        if not chat_name:
            return jsonify({"error": "Missing 'name' field"}), 
        doc = {
            "_id": chat_name,
        }
        try:
            db["active_chats"].insert_one(doc)
            return "", 201

        except DuplicateKeyError:
            return "", 409


    # get available chats
    @app.route("/available_chats", methods=["GET"])
    async def get_available_chats():

        # Init Telethon client
        telegram_client = TelegramClient('rent-scraper',
                            app.config["telegram"]["api_id"],
                            app.config["telegram"]["app_hash"],
                            )
        await telegram_client.start()

        dialog_names = []
        async for dialog in telegram_client.iter_dialogs():
            dialog_names.append(dialog.name)

        telegram_client.disconnect()
        return jsonify(dialog_names)


    # Sync messages
    @app.route("/sync_messages", methods=["POST"])
    async def sync_messages():
        
        # Init Telethon client
        telegram_client = TelegramClient('rent-scraper',
                            app.config["telegram"]["api_id"],
                            app.config["telegram"]["app_hash"],
                            )
        await telegram_client.start() 

        result_stats = {}
        active_chats = list(map(lambda x: x["_id"], db["active_chats"].find({})))
        
        async for dialog in telegram_client.iter_dialogs():
            if (dialog.name not in active_chats):
                continue
            chat_name = dialog.name

            # Get new messages
            last_id = db_get_last_message_id(db, chat_name)
            print(f"{dialog.name} - last id: {last_id}")

            messages = []
            async for msg in telegram_client.iter_messages(dialog,
                                                           min_id=last_id,
                                                           limit=100,
                                                           ):
                messages.append(msg)
            
            # Store messages
            print(f"- storing {len(messages)} messages")
            result_stats[chat_name] = db_store_messages_batch(db, chat_name, messages)
        
        telegram_client.disconnect()
        return jsonify(result_stats), 200

    # Gets all non-processed telegram messages and processes them. 
    @app.route("/run_pipeline", methods=["POST"])
    def run_pipeline():

        # start timer for metrics
        start = time.perf_counter()
    
        # get gemini key if present
        if app.config["gemini"]:
            gemini_key = app.config["gemini"]["api_key"]

        processed_count = 0
        
        # Get all collections that contain messages (assuming they follow a pattern like chat names)
        active_chats = list(map(lambda x: x["_id"], db["active_chats"].find({})))
    
        results = []
        
        for chat_name in active_chats:
            # Find all unprocessed messages
            unprocessed_messages = db["messages"].find({"__processed": {"$ne": True}})

            for message in unprocessed_messages:
                # Process the message
                results.append(process_message(db, message, model="ollama", gemini_key=gemini_key))
                #results.append(process_message(db, message, model="gemini", gemini_key=gemini_key))
                
                # Mark as processed
                db["messages"].update_one(
                    {"_id": message["_id"]}, 
                    {"$set": {"__processed": True, "extracted_features": results[-1]["extracted_features"]}}
                )
                processed_count += 1
                print(f"Processed {processed_count} messages.")
      
        end = time.perf_counter()
        elapsed = end - start  # seconds as float

        print(f"Processed {processed_count} messages in {elapsed:.6f} seconds.")
        return jsonify({"processed_messages": results, "elapsed_time": elapsed }), 200



    # Returns the total number of messages
    @app.route("/messages/count/total", methods=["GET"])
    def get_total_messages_count():
        count = db["messages"].count_documents({})
        return jsonify({"count": count}), 200

    # Returns the number of processed messages
    @app.route("/messages/count/processed", methods=["GET"])
    def get_processed_messages_count():
        count = db["messages"].count_documents({"__processed": True})
        return jsonify({"count": count}), 200


    # Returns all processed messages
    @app.route("/processed_messages", methods=["GET"])
    def fetch_processed_message():
        
        processed_messages = db["messages"].find(
            {"extracted_features": {"$ne": None}},
            {"extracted_features": 1, "date": 1, "_id": 0} 
        )
        
        # By default, the find method returns a cursor, so we need to iterate on it
        results = []
        for msg in processed_messages:
            tmp = msg["extracted_features"]
            tmp["date"] = msg["date"]
            results.append(tmp)
        return jsonify(results), 200


    # Manually extract data from single message, mostly for testing purposes
    @app.route("/extract", methods=["GET"])
    def extract():
        msg = request.get_json(force=True)["message"]
        res = process_message(db, msg)
        return jsonify(res), 200
    return app


if __name__ == "__main__":
    app = init_app()
    app.run(host="0.0.0.0", port="9009")
