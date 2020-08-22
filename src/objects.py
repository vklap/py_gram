from dataclasses import dataclass
from enum import Enum
from typing import Dict, Type
import abc
import dataclasses
import datetime


class ChatType(Enum):
    PRIVATE = 'private'
    GROUP = 'group'
    SUPERGROUP = 'supergroup'
    CHANNEL = 'channel'


class AbstractObject(abc.ABC):
    @abc.abstractmethod
    def to_dict(self) -> Dict:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def from_dict(cls, data: Dict) -> 'AbstractObject':
        raise NotImplementedError


@dataclass
class User(AbstractObject):
    """
    https://core.telegram.org/bots/api#user
    """
    id: int
    is_bot: bool
    first_name: str

    def to_dict(self) -> Dict:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        return cls(**data)


@dataclass
class Chat(AbstractObject):
    """
    https://core.telegram.org/bots/api#chat
    """
    id: int
    type: ChatType

    def __post_init__(self):
        self.type = ChatType(self.type)

    def to_dict(self) -> Dict:
        data = dataclasses.asdict(self)
        data['type'] = data['type'].value
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'Chat':
        return cls(**data)


@dataclass
class Message(AbstractObject):
    """
    https://core.telegram.org/bots/api#message
    """
    message_id: int
    from_user: User
    date: int
    chat: Chat

    def to_dict(self) -> Dict:
        data = dataclasses.asdict(self)
        data['user'] = data.pop('from_user')
        data['chat']['type'] = data['chat']['type'].value
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'AbstractObject':
        user = data.pop('user')
        return cls(from_user=user, **data)
