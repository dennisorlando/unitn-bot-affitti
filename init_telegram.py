from telethon import TelegramClient
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

telegram_client = TelegramClient('rent-scraper',
                            config["telegram"]["api_id"],
                            config["telegram"]["app_hash"],
                            )
telegram_client.start() 
