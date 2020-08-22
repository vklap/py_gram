from typing import Dict, Union, List
import abc
import asyncio
from pprint import pprint

import httpx

from src import objects

# https://core.telegram.org/bots/api


class AbstractTelegramClient:
    BASE_URL_FORMAT = 'https://api.telegram.org/bot{token}'

    def __init__(self):
        self.updates_queue = asyncio.Queue()

    async def start_updates_worker(self):
        update = None
        self.updates_queue.put_nowait(None)
        while True:
            update_id = await self.updates_queue.get()
            updates = await self.get_updates(update_id)
            for update in updates:
                await self._receive_update(update)
            update_id = update.update_id + 1 if update else None
            self.updates_queue.task_done()
            self.updates_queue.put_nowait(update_id)

    @property
    @abc.abstractmethod
    def bot_token(self) -> str:
        raise NotImplementedError

    @property
    def _base_url(self) -> str:
        return self.BASE_URL_FORMAT.format(token=self.bot_token)

    async def get_me(self) -> Dict:
        url = f'{self._base_url}/getMe'
        data = await self._execute_get(url)
        pprint(data)
        return data

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

    async def _receive_update(self, update: objects.Update) -> None:
        asyncio.create_task(self._handle_update(update))

    @abc.abstractmethod
    async def _handle_update(self, update: objects.Update) -> None:
        raise NotImplementedError


class TelegramClient(AbstractTelegramClient):
    def __init__(self, bot_token):
        super().__init__()
        self._bot_token = bot_token

    @property
    def bot_token(self) -> str:
        return self._bot_token

    async def _handle_update(self, update: objects.Update) -> None:
        print(update.update_id, update.message.text)


if __name__ == '__main__':
    import dotenv
    import os
    dotenv.load_dotenv()
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    # print(BOT_TOKEN)
    client = TelegramClient(BOT_TOKEN)
    asyncio.run(client.get_me())
    asyncio.run(client.start_updates_worker())
    print('finished')
