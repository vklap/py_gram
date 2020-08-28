from pytest_httpx import HTTPXMock
import pytest

from src.client import ClientError
from src.client import TelegramClient


class TestTelegramClient:
    BOT_TOKEN = 'test-token'
    BASE_URL = TelegramClient.BASE_URL_FORMAT.format(bot_token=BOT_TOKEN)

    @pytest.fixture
    def client(self) -> TelegramClient:
        return TelegramClient(self.BOT_TOKEN)

    @pytest.mark.asyncio
    async def test_get_me(self, client, httpx_mock: HTTPXMock):
        url = f'{self.BASE_URL}/getMe'
        expected_result = {'key': 'value'}
        httpx_mock.add_response(url=url, json=expected_result)

        result = await client.get_me()

        assert result == expected_result
