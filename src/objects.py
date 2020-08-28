from enum import Enum
from typing import Dict, List, Type
import abc
import dataclasses
import inspect
import typing


class ChatType(Enum):
    PRIVATE = 'private'
    GROUP = 'group'
    SUPERGROUP = 'supergroup'
    CHANNEL = 'channel'


class MessageEntityType(Enum):
    MENTION = 'mention'
    HASHTAG = 'hashtag'
    CASHTAG = 'cashtag'
    BOT_COMMAND = 'bot_command'
    URL = 'url'
    EMAIL = 'email'
    PHONE_NUMBER = 'phone_number'
    BOLD = 'bold'
    ITALIC = 'italic'
    UNDERLINE = 'underline'
    STRIKETHROUGH = 'strikethrough'
    CODE = 'code'
    PRE = 'pre'
    TEXT_LINK = 'text_link'
    TEXT_MENTION = 'text_mention'


class User:
    """
    https://core.telegram.org/bots/api#user
    """

    def __init__(self, id: int, is_bot: bool, first_name: str, **kwargs):
        self.first_name = first_name
        self.id = id
        self.is_bot = is_bot
        self.kwargs = kwargs

    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        return cls(**data)

    def __repr__(self):
        return f'<User(id={self.id}, is_bot={self.is_bot}, first_name={self.first_name})>'


class Chat:
    """
    https://core.telegram.org/bots/api#chat
    """

    def __init__(self, id: int, type: str, first_name: str = None, last_name: str = None, **kwargs):
        self.first_name = first_name
        self.id = id
        self.kwargs = kwargs
        self.last_name = last_name
        self.type = type

    @classmethod
    def from_dict(cls, data: Dict) -> 'Chat':
        return cls(**data)

    def __repr__(self):
        return f'<Chat(id={self.id}, type={self.type}, first_name={self.first_name})>'


class Message:
    """
    https://core.telegram.org/bots/api#message
    """

    def __init__(self, message_id: int, from_user: User, date: int, chat: Chat, text: str = None, **kwargs):
        self.chat = chat
        self.date = date
        self.from_user = from_user
        self.kwargs = kwargs
        self.message_id = message_id
        self.text = text

    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        from_user = data.pop('from')
        chat_data = data.pop('chat')
        user = User.from_dict(from_user)
        chat = Chat.from_dict(chat_data)
        return cls(from_user=user, chat=chat, **data)

    def __repr__(self):
        return f'<Message(message_id={self.message_id}, text={self.text}, chat={self.chat}, user={self.from_user})>'


class CallbackQuery:
    """
    https://core.telegram.org/bots/api#callbackquery
    """
    def __init__(self, id: str, from_user: User, message: Message = None,
                 inline_message_id: str = None, chat_instance: str = None,
                 data: str = None, game_short_name: str = None):
        self.game_short_name = game_short_name
        self.data = data
        self.chat_instance = chat_instance
        self.inline_message_id = inline_message_id
        self.message = message
        self.from_user = from_user
        self.id = id

    def __repr__(self):
        return f'<CallbackQuery(id={self.id}, data={self.data}, from={self.from_user}, message={self.message})>'

    @classmethod
    def from_dict(cls, data: Dict) -> 'CallbackQuery':
        from_user = data.pop('from')
        user = User.from_dict(from_user)
        try:
            message_data = data.pop('message')
        except KeyError:
            message = None
        else:
            message = Message.from_dict(message_data)
        return cls(from_user=user, message=message, **data)


class Update:
    """
    https://core.telegram.org/bots/api#update
    """

    def __init__(self, update_id: int, message: Message, callback_query: CallbackQuery, **kwargs):
        self.callback_query = callback_query
        self.kwargs = kwargs
        self.message = message
        self.update_id = update_id

    @classmethod
    def from_dict(cls, data: Dict) -> 'Update':
        try:
            message_data = data.pop('message')
        except KeyError:
            message = None
        else:
            message = Message.from_dict(message_data)

        try:
            callback_query_data = data.pop('callback_query')
        except KeyError:
            callback_query = None
        else:
            callback_query = CallbackQuery.from_dict(callback_query_data)
        return cls(message=message, callback_query=callback_query, **data)

    def __repr__(self):
        return f'<Update(update_id={self.update_id}, message={self.message})'


class InlineKeyboardButton:
    def __init__(self, text: str, callback_data: str = None, url: str = None):
        self.url = url
        self.callback_data = callback_data
        self.text = text

    def __repr__(self):
        return f'<InlineKeyboardButton(text={self.text}, callback_data={self.callback_data}, url={self.url})>'

    def to_dict(self) -> Dict:
        data = {'text': self.text}
        if self.url:
            data['url'] = self.url
        if self.callback_data:
            data['callback_data'] = self.callback_data
        return data


class KeyboardMarkup(abc.ABC):
    @abc.abstractmethod
    def to_dict(self) -> Dict:
        raise NotImplementedError


class InlineKeyboardMarkup(KeyboardMarkup):
    def __init__(self, inline_keyboard: List[InlineKeyboardButton]):
        self.inline_keyboard = inline_keyboard if inline_keyboard else []

    def __repr__(self):
        return f'<InlineKeyboardMarkup(inline_keyboard={self.inline_keyboard})>'

    def to_dict(self) -> Dict:
        return {'inline_keyboard': [[button.to_dict() for button in self.inline_keyboard]]}
