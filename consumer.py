import dotenv
import os
from src.client import TelegramClient


if __name__ == '__main__':
    dotenv.load_dotenv()
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    client = TelegramClient(BOT_TOKEN)
    client.start_listening_for_updates()
    print('finished')
