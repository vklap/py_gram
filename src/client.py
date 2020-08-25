import json
from pprint import pprint
from typing import Dict, Union, List
import abc
import asyncio
import atexit

import httpx

from src import objects


# https://core.telegram.org/bots/api


class AbstractTelegramClient(abc.ABC):
    SENTINEL = object()
    BASE_URL_FORMAT = 'https://api.telegram.org/bot{token}'

    def __init__(self):
        atexit.register(self.handle_exit)
        self.queue = asyncio.Queue()
        self.loop = asyncio.get_event_loop()
        self.event = asyncio.Event()
        self.listen_task = None

    def handle_exit(self):
        task = self.loop.create_task(self.queue.put(self.SENTINEL))
        self.loop.run_until_complete(task)
        pending = asyncio.all_tasks(loop=self.loop)
        for task in pending:
            task.cancel()
        group = asyncio.gather(*pending, loop=self.loop, return_exceptions=True)
        self.loop.run_until_complete(group)
        self.loop.close()

    def start_listening_for_updates(self):
        asyncio.run(self.start_updates_worker())

    async def start_updates_worker(self):
        update = None
        self.queue.put_nowait(None)
        while True:
            update_id = await self.queue.get()
            if update_id == self.SENTINEL:
                break
            updates = await self.get_updates(update_id)
            for update in updates:
                await self._receive_update(update)
            update_id = update.update_id + 1 if update else None
            self.queue.task_done()
            self.queue.put_nowait(update_id)

    @property
    @abc.abstractmethod
    def bot_token(self) -> str:
        raise NotImplementedError

    @property
    def _base_url(self) -> str:
        return self.BASE_URL_FORMAT.format(token=self.bot_token)

    async def get_me(self) -> Dict:
        url = f'{self._base_url}/getMe'
        return await self._execute_get(url)

    async def send_message(self, chat_id: Union[int, str], text: str, reply_markup=None) -> objects.Message:
        url = f'{self._base_url}/sendMessage'
        data = {
            'chat_id': chat_id,
            'text': text,
        }
        if reply_markup:
            data['reply_markup'] = json.dumps(reply_markup.to_dict())
            # data['reply_markup'] = reply_markup.to_dict()
        result = await self._execute_post(url, data)
        if result['ok'] is True:
            return objects.Message.from_dict(result['result'])
        else:
            raise Exception()

    async def get_updates(self, update_id: int = None) -> List[objects.Update]:
        params = {}
        if update_id is not None:
            params['offset'] = update_id

        url = f'{self._base_url}/getUpdates'
        data = await self._execute_get(url, params=params)
        updates = []
        if data['ok'] is True:
            for result in data['result']:
                update = objects.Update.from_dict(result)
                updates.append(update)

        return updates

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
        asyncio.create_task(self._handle_update(update))

    @abc.abstractmethod
    async def _handle_update(self, update: objects.Update) -> None:
        raise NotImplementedError


class TelegramClient(AbstractTelegramClient):
    def __init__(self, bot_token):
        super().__init__()
        self._bot_token = bot_token
        self.responded = False

    @property
    def bot_token(self) -> str:
        return self._bot_token

    async def _handle_update(self, update: objects.Update) -> None:
        print(update)
        if not self.responded:
            self.responded = True
            await self.send_message(chat_id=update.message.chat.id, text='This is a response!')
