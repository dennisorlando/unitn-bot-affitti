import yaml
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, jsonify, request, Response
from telethon import TelegramClient

from db_helpers import db_store_messages_batch, db_get_last_message_date

def init_app():
    app = Flask(__name__)

    # Init config
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    app.config["telegram"] = config["telegram"]
    print(app.config["telegram"])
    
    # Init mongodb client
    mdb_client = MongoClient("mongodb://localhost:27017", 
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
    @app.route("/sync", methods=["POST"])
    async def sync_messages():
        # Init Telethon client
        telegram_client = TelegramClient('rent-scraper',
                            app.config["telegram"]["api_id"],
                            app.config["telegram"]["app_hash"],
                            )
        await telegram_client.start()

        result_stats = {}
        active_chats = list(map(lambda x: x["_id"], db["active_chats"].find({})))
        print(active_chats)
        async for dialog in telegram_client.iter_dialogs():
            if (dialog.name not in active_chats):
                continue
            chat_name = dialog.name

            # Get new messages
            last_date = db_get_last_message_date(db, chat_name)

            messages = []
            async for msg in telegram_client.iter_messages(dialog,
                                                           offset_date=last_date,
                                                           limit=30,
                                                           reverse=True,
                                                           ):
                print(f"Working on {msg.message}")
                if last_date and msg.date.replace(tzinfo=None) <= last_date: # filter out the lower bound
                    continue
                messages.append(msg)
            
            # Store messages
            print(f"storing {len(messages)} messages")
            result_stats[chat_name] = db_store_messages_batch(db, chat_name, messages)
        
        telegram_client.disconnect()
        return jsonify(result_stats), 200



    return app


if __name__ == "__main__":
    app = init_app()
    app.run(host="0.0.0.0", port="9009")
