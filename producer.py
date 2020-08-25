from datetime import datetime
import asyncio
import os

import dotenv

from src import objects
from src.client import TelegramClient


if __name__ == '__main__':
    dotenv.load_dotenv()
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    client = TelegramClient(BOT_TOKEN)
    asyncio.run(client.send_message(
        chat_id=1220644883,
        text=f'Hello Victor {datetime.now()}',
        reply_markup=objects.InlineKeyboardMarkup(inline_keyboard=[
            objects.InlineKeyboardButton(text='Google Me', url='https://www.google.com?q=victor.klapholz'),
            objects.InlineKeyboardButton(text='Click Me', callback_data='clicked_me'),
        ])
    ))

    # asyncio.run(client.send_message(chat_id=1220644883, text=f'/start'))
    print('finished')
