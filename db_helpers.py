from datetime import datetime


def db_get_last_message_date(db, chat_name):
    last_message = db["messages"].find({"chat_name": chat_name}).sort("date", -1).limit(1)
    last_message = list(last_message)
    return last_message[0]["date"] if last_message else None

def db_store_messages_batch(db, chat_name, messages):
    docs = []
    for msg in messages:
        docs.append({
            "chat_name": chat_name,
            "message_id": msg.id,
            "date": msg.date,
            "text": msg.message,
        })

    if docs:
        db["messages"].insert_many(docs)
    return len(docs)

