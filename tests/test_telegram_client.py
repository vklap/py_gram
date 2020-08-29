from datetime import datetime
import asyncio
import threading

from pytest_httpx import HTTPXMock
import pytest

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

    @pytest.mark.asyncio
    async def test_get_updates(self, client, httpx_mock: HTTPXMock):
        user = objects.User(id=1, is_bot=True, first_name='SuperBot')
        chat = objects.Chat(id=1965, chat_type=objects.ChatType.PRIVATE, first_name='John', last_name='Doe')
        message = objects.Message(message_id=506, from_user=user, date=int(datetime.utcnow().timestamp()), chat=chat)
        update = objects.Update(update_id=88, message=message)
        response = {
            'ok': True,
            'result': [{
                'update_id': update.update_id,
                'message': {
                    'message_id': message.message_id,
                    'date': message.date,
                    'from': {'id': user.id, 'is_bot': True, 'first_name': user.first_name},
                    'chat': {'id': chat.id, 'type': chat.chat_type.value, 'first_name': chat.first_name, 'last_name': chat.last_name},
                },
            }],
        }
        url = f'{self.BASE_URL}/getUpdates?offset={update.update_id}'
        httpx_mock.add_response(url=url, json=response)

        result = await client.get_updates(update.update_id)

        assert len(result) == 1
        received_update = result[0]
        assert received_update.update_id == update.update_id
        assert received_update.message.message_id == message.message_id
        assert received_update.message.chat.id == message.chat.id
        assert received_update.message.chat.chat_type == message.chat.chat_type

    @pytest.mark.asyncio
    async def test_start_listening_for_updates_for_message(self, client, httpx_mock: HTTPXMock):
        user = objects.User(id=1, is_bot=True, first_name='SuperBot')
        chat = objects.Chat(id=1965, chat_type=objects.ChatType.PRIVATE, first_name='John', last_name='Doe')
        message = objects.Message(message_id=506, from_user=user, date=int(datetime.utcnow().timestamp()), chat=chat)
        update = objects.Update(update_id=88, message=message)
        response = {
            'ok': True,
            'result': [{
                'update_id': update.update_id,
                'message': {
                    'message_id': message.message_id,
                    'date': message.date,
                    'from': {'id': user.id, 'is_bot': True, 'first_name': user.first_name},
                    'chat': {'id': chat.id, 'type': chat.chat_type.value, 'first_name': chat.first_name, 'last_name': chat.last_name},
                },
            }],
        }

        url = f'{self.BASE_URL}/getUpdates'
        httpx_mock.add_response(url=url, json=response)

        handled_message: objects.Message = None

        def message_handler(c: TelegramClient, msg: objects.Message) -> None:
            nonlocal handled_message
            handled_message = msg

        client.register_message_handler(message_handler)
        thread = threading.Thread(target=client.start_listening_for_updates)
        thread.start()
        thread.join()

        assert handled_message.message_id == message.message_id
