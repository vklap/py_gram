from typing import Dict
import abc
import asyncio
from pprint import pprint

import httpx

# https://core.telegram.org/bots/api


class AbstractTelegramClient:
    BASE_URL_FORMAT = 'https://api.telegram.org/bot{token}'

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

    @classmethod
    async def _execute_get(cls, url: str, params: Dict = None) -> Dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
        return response.json()


class TelegramClient(AbstractTelegramClient):
    def __init__(self, bot_token):
        self._bot_token = bot_token

    @property
    def bot_token(self) -> str:
        return self._bot_token


if __name__ == '__main__':
    import dotenv
    import os
    dotenv.load_dotenv()
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    # print(BOT_TOKEN)
    client = TelegramClient(BOT_TOKEN)
    asyncio.run(client.get_me())
