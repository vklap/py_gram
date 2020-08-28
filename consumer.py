import os

import dotenv

from src import objects
from src.client import TelegramClient


async def handle_message(client: TelegramClient, message: objects.Message) -> None:
    await client.send_message(message.chat.id, text=message.text.upper())


async def handle_callback_query(client: TelegramClient, callback_query: objects.CallbackQuery) -> None:
    await client.answer_callback_query(callback_query.id, text='Thank you!', show_alert=True)


async def handle_command(client: TelegramClient, command: str, message: objects.Message) -> None:
    await client.send_message(message.chat.id, text=f'Got a command {command}')


if __name__ == '__main__':
    dotenv.load_dotenv()
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    telegram_client = TelegramClient(BOT_TOKEN)
    telegram_client.register_command_handler('/sudo', handle_command)
    telegram_client.register_message_handler(handle_message)
    telegram_client.register_callback_query_handler(handle_callback_query)
    telegram_client.start_listening_for_updates()
    print('started listening...')
