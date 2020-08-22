from dataclasses import dataclass
from enum import Enum
from typing import Dict, List
import abc
import dataclasses


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
    last_name: str = None

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
    first_name: str = None
    last_name: str = None

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
class MessageEntity(AbstractObject):
    """
    https://core.telegram.org/bots/api#messageentity
    """
    offset: int
    length: int
    type: str
    url: str = None
    user: User = None
    language: str = None

    def to_dict(self) -> Dict:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'MessageEntity':
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
    text: str = None
    entities: List[MessageEntity] = dataclasses.field(default_factory=list)

    def to_dict(self) -> Dict:
        data = dataclasses.asdict(self)
        data['user'] = data.pop('from_user')
        data['chat']['type'] = data['chat']['type'].value
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        try:
            user = data.pop('from_user')
        except KeyError:
            try:
                user = data.pop('user')
            except KeyError:
                user = data.pop('from')
        return cls(from_user=user, **data)


@dataclass
class Update(AbstractObject):
    """
    https://core.telegram.org/bots/api#update
    """
    update_id: int
    message: Message

    def to_dict(self) -> Dict:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'AbstractObject':
        message = data['message']
        message['from_user'] = message.pop('from')
        return cls(**data)


if __name__ == '__main__':
    import pprint
    message = {'chat': {'first_name': 'Victor', 'id': 1220644883, 'last_name': 'Klapholz', 'type': 'private'},
               'date': 1598108694, 'entities': [{'length': 6, 'offset': 0, 'type': 'bot_command'}],
               'from': {'first_name': 'Victor', 'id': 1220644883, 'is_bot': False, 'last_name': 'Klapholz'},
               'message_id': 1, 'text': '/start'}
    # pprint.pprint(Message.from_dict(message))

    update = {'message': {'chat': {'first_name': 'Victor',
                                   'id': 1220644883,
                                   'last_name': 'Klapholz',
                                   'type': 'private'},
                          'date': 1598108694,
                          'entities': [{'length': 6, 'offset': 0, 'type': 'bot_command'}],
                          'from': {'first_name': 'Victor',
                                   'id': 1220644883,
                                   'is_bot': False,
                                   'last_name': 'Klapholz'},
                          'message_id': 1,
                          'text': '/start'},
              'update_id': 520450359}

    pprint.pprint(Update.from_dict(update))
