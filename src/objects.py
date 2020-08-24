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


class Update:
    """
    https://core.telegram.org/bots/api#update
    """
    def __init__(self, update_id: int, message: Message, **kwargs):
        self.kwargs = kwargs
        self.message = message
        self.update_id = update_id

    @classmethod
    def from_dict(cls, data: Dict) -> 'Update':
        message_data = data.pop('message')
        message = Message.from_dict(message_data)
        return cls(message=message, **data)

    def __repr__(self):
        return f'<Update(update_id={self.update_id}, message={self.message})'
