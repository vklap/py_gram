from pytest_httpx import HTTPXMock
import pytest
import pytest_asyncio

from src import objects
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
        user = objects.User(id=1, is_bot=True, first_name='SuperBot')
        response = {
            'ok': True,
            'result': {'id': user.id, 'is_bot': True, 'first_name': user.first_name},
        }
        httpx_mock.add_response(url=url, json=response)

        result = await client.get_me()

        assert result.id == user.id
        assert result.is_bot == user.is_bot
        assert result.first_name == user.first_name

    @pytest.mark.asyncio
    async def test_get_me_that_fails(self, client, httpx_mock: HTTPXMock):
        url = f'{self.BASE_URL}/getMe'
        error_description = 'some error'
        response = {
            'ok': False,
            'description': error_description,
        }
        httpx_mock.add_response(url=url, json=response)

        with pytest.raises(ClientError) as e:
            await client.get_me()

        assert str(e.value) == error_description
