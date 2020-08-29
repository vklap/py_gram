from datetime import datetime
from typing import Tuple, Dict
import threading

from pytest_httpx import HTTPXMock
import pytest

from src import objects
from src.client import ClientError
from src.client import TelegramClient


class TestTelegramClient:
    BOT_TOKEN = 'test-token'
    BASE_URL = TelegramClient.BASE_URL_FORMAT.format(bot_token=BOT_TOKEN)

    @classmethod
    def _create_response_for_update(cls, command_name: str = None,
                                    is_callback_query: bool = False) -> Tuple[Dict, objects.Update]:
        command_text = f'{command_name}@SuperBot'
        user = objects.User(id=1, is_bot=True, first_name='SuperBot')
        chat = objects.Chat(id=1965, chat_type=objects.ChatType.PRIVATE, first_name='John', last_name='Doe')
        message_entity = objects.MessageEntity(
            message_entity_type=objects.MessageEntityType.BOT_COMMAND,
            offset=0,
            length=len(command_name),
        ) if command_name else None
        text = f'{command_text} whatever' if command_text else None
        message = objects.Message(message_id=506, from_user=user, date=int(datetime.utcnow().timestamp()), chat=chat,
                                  entities=[message_entity], text=text)
        callback_query_data = 'some-data'
        callback_query = objects.CallbackQuery(id=1924, from_user=user, message=message, data=callback_query_data)
        update = objects.Update(update_id=88, message=message, callback_query=callback_query)
        message_response = {
            'message_id': message.message_id,
            'date': message.date,
            'from': {'id': user.id, 'is_bot': True, 'first_name': user.first_name},
            'chat': {
                'id': chat.id,
                'type': chat.chat_type.value,
                'first_name': chat.first_name,
                'last_name': chat.last_name,
            },
            'text': message.text,
        }

        if command_name:
            message_response['entities'] = [{
                'type': message_entity.message_entity_type.value,
                'offset': message_entity.offset,
                'length': message_entity.length,
            }]

        update_response = {
            'update_id': update.update_id,
            'message': message_response,
        }
        if is_callback_query:
            update_response['callback_query'] = {
                'id': callback_query.id,
                'from': message_response['from'],
                'message': message_response,
                'data': callback_query.data,
            }

        response = {
            'ok': True,
            'result': [update_response],
        }
        return response, update

    @pytest.fixture
    def client(self) -> TelegramClient:
        client = TelegramClient(self.BOT_TOKEN)
        yield client
        client.handle_exit()

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
        response, update = self._create_response_for_update()
        url = f'{self.BASE_URL}/getUpdates?offset={update.update_id}'
        httpx_mock.add_response(url=url, json=response)

        result = await client.get_updates(update.update_id)

        assert len(result) == 1
        received_update = result[0]
        assert received_update.update_id == update.update_id
        assert received_update.message.message_id == update.message.message_id
        assert received_update.message.chat.id == update.message.chat.id
        assert received_update.message.chat.chat_type == update.message.chat.chat_type

    @pytest.mark.asyncio
    async def test_start_listening_for_updates_for_message(self, client, httpx_mock: HTTPXMock):
        response, update = self._create_response_for_update()
        url = f'{self.BASE_URL}/getUpdates'
        httpx_mock.add_response(url=url, json=response)

        handled_message: objects.Message = None

        async def message_handler(c: TelegramClient, msg: objects.Message) -> None:
            nonlocal handled_message
            handled_message = msg

        client.register_message_handler(message_handler)
        thread = threading.Thread(target=client.start_listening_for_updates)
        thread.start()
        thread.join()

        assert handled_message.message_id == update.message.message_id

    @pytest.mark.asyncio
    async def test_start_listening_for_updates_for_command(self, client, httpx_mock: HTTPXMock):
        command_name = '/my_command'
        response, update = self._create_response_for_update(command_name)
        url = f'{self.BASE_URL}/getUpdates'
        httpx_mock.add_response(url=url, json=response)

        handled_message: objects.Message = None
        handled_command: str = None

        async def command_handler(c: TelegramClient, cmd: str, msg: objects.Message) -> None:
            nonlocal handled_message
            nonlocal handled_command
            handled_command = cmd
            handled_message = msg

        client.register_command_handler(command_name, command_handler)
        thread = threading.Thread(target=client.start_listening_for_updates)
        thread.start()
        thread.join()

        assert handled_message.message_id == update.message.message_id
        assert handled_command == command_name

    @pytest.mark.asyncio
    async def test_start_listening_for_updates_for_callback_query(self, client, httpx_mock: HTTPXMock):
        response, update = self._create_response_for_update(is_callback_query=True)
        url = f'{self.BASE_URL}/getUpdates'
        httpx_mock.add_response(url=url, json=response)

        handled_callback: objects.CallbackQuery = None

        async def callback_query_handler(c: TelegramClient, callback: objects.CallbackQuery) -> None:
            nonlocal handled_callback
            handled_callback = callback

        client.register_callback_query_handler(callback_query_handler)
        thread = threading.Thread(target=client.start_listening_for_updates)
        thread.start()
        thread.join()

        assert handled_callback.id == update.callback_query.id
        assert handled_callback.data == update.callback_query.data
        assert handled_callback.message.message_id == update.callback_query.message.message_id
        assert handled_callback.from_user.id == update.callback_query.from_user.id

    @pytest.mark.asyncio
    async def test_send_message(self, client, httpx_mock: HTTPXMock):
        message_id = 566
        chat_id = 88
        response = {
            'ok': True,
            'result': {
                'message_id': message_id,
                'date': datetime.utcnow().timestamp(),
                'chat': {'id': chat_id, 'type': objects.ChatType.PRIVATE.value},
                'from': {'id': 1962, 'is_bot': True, 'first_name': 'TheBot'}
            },
        }

        url = f'{self.BASE_URL}/sendMessage'
        httpx_mock.add_response(url=url, json=response)

        keyboard_markup = objects.InlineKeyboardMarkup([
            objects.InlineKeyboardButton(text='a text', callback_data='callback data', url='https://some-url'),
        ])

        result = await client.send_message(chat_id, text='some text', keyboard_markup=keyboard_markup)

        assert result.message_id == message_id

    @pytest.mark.asyncio
    async def test_send_photo_url(self, client, httpx_mock: HTTPXMock):
        photo_url = 'https://photo_url'
        message_id = 566
        chat_id = 88
        response = {
            'ok': True,
            'result': {
                'message_id': message_id,
                'date': datetime.utcnow().timestamp(),
                'chat': {'id': chat_id, 'type': objects.ChatType.PRIVATE.value},
                'from': {'id': 1962, 'is_bot': True, 'first_name': 'TheBot'}
            },
        }

        url = f'{self.BASE_URL}/sendPhoto'
        httpx_mock.add_response(url=url, json=response)

        keyboard_markup = objects.InlineKeyboardMarkup([
            objects.InlineKeyboardButton(text='a text', callback_data='callback data', url='https://some-url'),
        ])
        caption = 'a' * 2_000
        result = await client.send_photo_url(chat_id, photo_url, caption, keyboard_markup=keyboard_markup,
                                             disable_notification=False, reply_to_message_id=message_id)

        assert result.message_id == message_id

    @pytest.mark.asyncio
    async def test_answer_callback_query(self, client, httpx_mock: HTTPXMock):
        response = {
            'ok': True,
            'result': True,
        }

        url = f'{self.BASE_URL}/answerCallbackQuery'
        httpx_mock.add_response(url=url, json=response)

        result = await client.answer_callback_query(
            callback_query_id=1,
            text='some text',
            show_alert=True,
            url='https://a-url',
            cache_time=1,
        )

        assert result is True
