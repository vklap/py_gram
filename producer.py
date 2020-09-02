from datetime import datetime
import asyncio
import os

import dotenv

from py_gram import objects
from py_gram.client import TelegramClient


if __name__ == '__main__':
    dotenv.load_dotenv()
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    client = TelegramClient(BOT_TOKEN)
    # asyncio.run(client.send_message(
    #     chat_id=1220644883,
    #     text=f'Hello Dude {datetime.now()}',
    #     keyboard_markup=objects.InlineKeyboardMarkup(inline_keyboard=[
    #         objects.InlineKeyboardButton(text='Google Me', url='https://www.google.com?q=dude'),
    #         objects.InlineKeyboardButton(text='Click Me', callback_data='clicked_me'),
    #     ])
    # ))
    asyncio.run(client.send_photo_url(
        chat_id=1220644883,
        photo_url='https://www.clementoni.com/media/prod/se/39514/tour-eiffel-1000-pcs-high-quality-collection_UdFFh2G.jpg',
        caption=f'Hello From Paris {datetime.now()}',
        keyboard_markup=objects.InlineKeyboardMarkup(inline_keyboard=[
            objects.InlineKeyboardButton(text='Google Me', url='https://www.google.com?q=Paris'),
            objects.InlineKeyboardButton(text='Click Me', callback_data='clicked_me'),
        ])
    ))
    # asyncio.run(client.send_message(chat_id=1220644883, text=f'/start'))
    print('finished')
