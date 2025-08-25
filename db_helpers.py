from datetime import datetime


def db_get_last_message_id(db, chat_name):
    last_message = db["messages"].find({"chat_name": chat_name}).sort("message_id", -1).limit(1)
    last_message = list(last_message)
    return last_message[0]["message_id"] if last_message else None

def db_store_messages_batch(db, chat_name, messages):
    docs = []
    for msg in messages:
        # Check for duplicates
        if db["messages"].find_one({"message_id": msg.id}):
            continue
        docs.append({
            "chat_name": chat_name,
            "message_id": msg.id,
            "date": msg.date,
            "text": msg.message,
        })

    if docs:
        db["messages"].insert_many(docs)
    return len(docs)



def db_get_unprocessed_messages(db):
    unprocessed_messages = db["messages"].find({"processed": {"$ne": True}})
    return list(unprocessed_messages)

def db_get_processed_messages(db):
    processed_messages = db["messages"].find({"processed": True})
    return list(processed_messages)

def db_get_all_messages(db):
    all_messages = db["messages"].find({})
    return list(all_messages)

def db_get_message_by_id(db, message_id):
    message = db["messages"].find_one({"message_id": message_id})
    return message

def db_update_message_clarification(db, message_id, clarification):
    db["messages"].update_one(
        {"message_id": message_id},
        {"$set": {"clarification": clarification}}
    )

def db_update_message_processed(db, message_id, extracted_features):
    db["messages"].update_one(
        {"message_id": message_id},
        {"$set": {"processed": True, "extracted_features": extracted_features}}
    )

def db_get_all_processed_rentals(db):
    rentals = db["messages"].find({"processed": True, "extracted_features": {"$ne": None}})
    return list(rentals)

def db_get_all_users(db):
    users = db["users"].find({})
    return list(users)

def db_get_user_by_id(db, user_id):
    user = db["users"].find_one({"user_id": user_id})
    return user

def db_update_user(db, user_id, update_data):
    db["users"].update_one(
        {"user_id": user_id},
        {"$set": update_data},
        upsert=True
    )

def db_get_last_date_check(db, chat_name):
    last_check = db["sync_log"].find_one({"chat_name": chat_name})
    return last_check["last_date_check"] if last_check else None

def db_update_last_date_check(db, chat_name, date):
    db["sync_log"].update_one(
        {"chat_name": chat_name},
        {"$set": {"last_date_check": date}},
        upsert=True
    )

def db_delete_message(db, message_id):
    db["messages"].delete_one({"message_id": message_id})

def db_delete_user(db, user_id):
    db["users"].delete_one({"user_id": user_id})

def db_delete_all_messages(db):
    db["messages"].delete_many({})

def db_delete_all_users(db):
    db["users"].delete_many({})

def db_delete_all_sync_logs(db):
    db["sync_log"].delete_many({})

def db_delete_all_data(db):
    db_delete_all_messages(db)
    db_delete_all_users(db)
    db_delete_all_sync_logs(db)

def db_get_all_data(db):
    return {
        "messages": db_get_all_messages(db),
        "users": db_get_all_users(db),
        "sync_log": list(db["sync_log"].find({}))
    }

def db_restore_data(db, data):
    db_delete_all_data(db)
    if "messages" in data and data["messages"]:
        db["messages"].insert_many(data["messages"])
    if "users" in data and data["users"]:
        db["users"].insert_many(data["users"])
    if "sync_log" in data and data["sync_log"]:
        db["sync_log"].insert_many(data["sync_log"])

def db_get_stats(db):
    return {
        "messages": db["messages"].count_documents({}),
        "users": db["users"].count_documents({}),
        "sync_log": db["sync_log"].count_documents({})
    }
    
def db_get_processed_rentals_with_features(db):
    rentals = db["messages"].find({
        "processed": True, 
        "extracted_features": {"$ne": None}
    })
    
    formatted_rentals = []
    for rental in rentals:
        features = rental.get("extracted_features", {})
        price = features.get("price_per_month")
        if price is None or price == 0:
            price = -1
            
        formatted_rentals.append({
            "message_id": rental["message_id"],
            "date": rental["date"].isoformat(),
            "text": rental["text"],
            "price_per_month": price,
            "room_type": features.get("room_type"),
            "location": features.get("location"),
            "target_gender": features.get("target_gender"),
            "target_audience": features.get("target_audience"),
            "available_from": features.get("available_from"),
            "contract_duration": features.get("contract_duration"),
            "utilities_included": features.get("utilities_included"),
            "amenities": features.get("amenities"),
            "other": features.get("other")
        })
        
    return formatted_rentals