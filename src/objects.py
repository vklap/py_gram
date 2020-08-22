from dataclasses import dataclass
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


class AbstractObject(abc.ABC):
    abstract_object_field_types_by_name: Dict[str, Type['AbstractObject']] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if issubclass(cls, AbstractObject):
            resolved_hints = typing.get_type_hints(cls)
            cls.abstract_object_field_types_by_name = {name: klass for name, klass in resolved_hints.items()
                                                       if inspect.isclass(klass) and issubclass(klass, AbstractObject)}

    @abc.abstractmethod
    def to_dict(self) -> Dict:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: Dict) -> 'AbstractObject':
        cls._pre_from_dict_setup(data)
        instance = cls(**data)
        for field in dataclasses.fields(instance):
            if field.name in cls.abstract_object_field_types_by_name:
                raw_field_value = getattr(instance, field.name)
                field_value = cls.abstract_object_field_types_by_name[field.name].from_dict(raw_field_value)
                setattr(instance, field.name, field_value)
        return instance

    @classmethod
    def _pre_from_dict_setup(cls, data: Dict) -> None:
        pass


@dataclass
class User(AbstractObject):
    """
    https://core.telegram.org/bots/api#user
    """
    id: int
    is_bot: bool
    first_name: str
    last_name: str = None
    language_code: str = None

    def to_dict(self) -> Dict:
        return dataclasses.asdict(self)


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
    def _pre_from_dict_setup(cls, data: Dict) -> None:
        data['from_user'] = data.pop('from')
        try:
            entities = data['entities']
        except KeyError:
            pass
        else:
            data['entities'] = [MessageEntity(**entity) for entity in entities]


@dataclass
class Update(AbstractObject):
    """
    https://core.telegram.org/bots/api#update
    """
    update_id: int
    message: Message

    def to_dict(self) -> Dict:
        return dataclasses.asdict(self)


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
