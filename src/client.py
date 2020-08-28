import collections
from typing import Dict, Union, List, Callable, Awaitable, DefaultDict
import asyncio
import atexit
import json
import os

import httpx

from src import objects


# https://core.telegram.org/bots/api

class ClientError(Exception):
    """
    Common Exception raise by the Telegram Client.
    """


class TelegramClient:
    SENTINEL = object()
    BASE_URL_FORMAT = 'https://api.telegram.org/bot{token}'

    def __init__(self, bot_token: str = None):
        self._bot_token = bot_token if bot_token else os.environ['bot_token']
        atexit.register(self.handle_exit)
        self._queue = asyncio.Queue()
        self._message_handlers: List[Callable[['TelegramClient', objects.Message], Awaitable[None]]] = []
        self._command_handlers: DefaultDict[
            str, List[Callable[['TelegramClient', str, objects.Message], Awaitable[None]]]] = collections.defaultdict(
            list)
        self._callback_query_handlers: List[Callable[['TelegramClient', objects.CallbackQuery], Awaitable[None]]] = []
        self._loop = asyncio.get_event_loop()

    def handle_exit(self):
        task = self._loop.create_task(self._queue.put(self.SENTINEL))
        self._loop.run_until_complete(task)
        pending = asyncio.all_tasks(loop=self._loop)
        for task in pending:
            task.cancel()
        group = asyncio.gather(*pending, loop=self._loop, return_exceptions=True)
        self._loop.run_until_complete(group)
        self._loop.close()

    def start_listening_for_updates(self):
        asyncio.run(self.start_updates_worker())

    async def start_updates_worker(self):
        update = None
        self._queue.put_nowait(None)
        while True:
            update_id = await self._queue.get()
            if update_id == self.SENTINEL:
                break
            updates = await self.get_updates(update_id)
            for update in updates:
                await self._receive_update(update)
            update_id = update.update_id + 1 if update else None
            self._queue.task_done()
            self._queue.put_nowait(update_id)

    @property
    def _base_url(self) -> str:
        return self.BASE_URL_FORMAT.format(token=self._bot_token)

    async def get_me(self) -> Dict:
        url = f'{self._base_url}/getMe'
        return await self._execute_get(url)

    async def send_message(self, chat_id: Union[int, str], text: str,
                           keyboard_markup: objects.KeyboardMarkup = None) -> objects.Message:
        url = f'{self._base_url}/sendMessage'
        data = {
            'chat_id': chat_id,
            'text': text,
        }
        if keyboard_markup:
            data['reply_markup'] = json.dumps(keyboard_markup.to_dict())
        result = await self._execute_post(url, data)
        self._raise_for_error(result)
        return objects.Message.from_dict(result['result'])

    async def send_photo_url(self, chat_id: Union[int, str], photo_url: str, caption: str = None,
                             keyboard_markup: objects.KeyboardMarkup = None, disable_notification: bool = None,
                             reply_to_message_id: int = None) -> objects.Message:
        url = f'{self._base_url}/sendPhoto'
        data = {
            'chat_id': chat_id,
            'photo': photo_url,
        }
        if caption:
            data['caption'] = caption[:1024]
        if disable_notification is not None:
            data['disable_notification'] = disable_notification
        if reply_to_message_id is not None:
            data['reply_to_message_id'] = reply_to_message_id
        if keyboard_markup:
            data['reply_markup'] = json.dumps(keyboard_markup.to_dict())
        result = await self._execute_post(url, data)
        self._raise_for_error(result)
        return objects.Message.from_dict(result['result'])

    async def get_updates(self, update_id: int = None) -> List[objects.Update]:
        params = {}
        if update_id is not None:
            params['offset'] = update_id

        url = f'{self._base_url}/getUpdates'
        data = await self._execute_get(url, params=params)
        updates = []
        self._raise_for_error(data)
        for result in data['result']:
            update = objects.Update.from_dict(result)
            updates.append(update)
        return updates

    async def answer_callback_query(self, callback_query_id: str, text: str = None, show_alert: bool = None,
                                    url: str = None, cache_time: int = None) -> Dict:
        data = {'callback_query_id': callback_query_id}
        if text:
            data['text'] = text

        if show_alert is not None:
            data['show_alert'] = show_alert

        if url:
            data['url'] = url

        if cache_time is not None:
            data['cache_time'] = cache_time

        post_url = f'{self._base_url}/answerCallbackQuery'
        result = await self._execute_post(post_url, data)
        return result

    @classmethod
    async def _execute_get(cls, url: str, params: Dict = None) -> Dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
        return response.json()

    @classmethod
    async def _execute_post(cls, url: str, data: Dict = None) -> Dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)
            response.raise_for_status()
        return response.json()

    async def _receive_update(self, update: objects.Update) -> None:
        if update.callback_query:
            await self._handle_callback_query(update.callback_query)
        else:
            if update.message.entities:
                command_entities = [entity
                                    for entity in update.message.entities
                                    if entity.message_entity_type == objects.MessageEntityType.BOT_COMMAND]
            else:
                command_entities = None

            if command_entities:
                for entity in command_entities:
                    command = update.message.text[entity.offset: entity.offset + entity.length]
                    await self._handle_command(command, update.message)
            else:
                await self._handle_message(update.message)

    def register_command_handler(self, command: str,
                                 handler: Callable[['TelegramClient', str, objects.Message], Awaitable[None]]) -> None:
        self._command_handlers[command].append(handler)

    def register_message_handler(self, handler: Callable[['TelegramClient', objects.Message], Awaitable[None]]) -> None:
        self._message_handlers.append(handler)

    def register_callback_query_handler(self, handler: Callable[
        ['TelegramClient', objects.CallbackQuery], Awaitable[None]]) -> None:
        self._callback_query_handlers.append(handler)

    async def _handle_message(self, message: objects.Message) -> None:
        for handler in self._message_handlers:
            await handler(self, message)

    async def _handle_command(self, command: str, message: objects.Message) -> None:
        for handler in self._command_handlers[command]:
            await handler(self, command, message)

    async def _handle_callback_query(self, callback_query: objects.CallbackQuery) -> None:
        for handler in self._callback_query_handlers:
            await handler(self, callback_query)

    @classmethod
    def _raise_for_error(cls, data: Dict) -> None:
        if not data['ok']:
            raise ClientError(data['description'])
