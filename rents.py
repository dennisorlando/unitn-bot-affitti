import os
import dotenv

from telethon import TelegramClient, events, sync

dotenv.load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

# Print first two characters of each followed by XX
print(f"API_ID: {api_id[:3] if api_id else ''}xxxxxxx")
print(f"API_HASH: {api_hash[:3] if api_hash else ''}xxxxxxx")

groups = [
    #"SPOTTED CERCA CASA 🏠",
    "CERCO/OFFRO Appartamenti Trento",
]

client = TelegramClient('rent-scraper', api_id, api_hash)
client.start()

print("Listing your groups/chats...")
for dialog in client.iter_dialogs():
    if dialog.is_group and dialog.name in groups:
        print("\n\n")
        print(dialog.name)
        for message in client.iter_messages(dialog, limit=10):
            if message.message != '':
                print(message.date)
                print(message.message)
