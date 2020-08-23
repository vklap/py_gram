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
    can_join_groups: bool = None
    can_read_all_group_messages: bool = None
    language_code: str = None
    last_name: str = None
    supports_inline_queries: bool = None
    username: str = None

    def to_dict(self) -> Dict:
        return dataclasses.asdict(self)


class Message(AbstractObject):
    def to_dict(self) -> Dict:
        pass


@dataclass
class Chat(AbstractObject):
    """
    https://core.telegram.org/bots/api#chat
    """
    id: int
    type: ChatType
    first_name: str = None
    last_name: str = None
    title: str = None
    username: str = None
    # photo: ChatPhoto = None
    description: str = None
    invite_link: str = None
    pinned_message: Message = None
    # permissions: ChatPermissions = None
    slow_mode_delay: int = None
    sticker_set_name: str = None
    can_set_sticker_set: bool = None

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
    type: MessageEntityType
    url: str = None
    user: User = None
    language: str = None

    def to_dict(self) -> Dict:
        data = dataclasses.asdict(self)
        data['type'] = self.type.value

    def _pre_from_dict_setup(cls, data: Dict) -> None:
        data['type'] = MessageEntityType(data['type'])


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
    forward_from: User = None
    forward_from_chat: Chat = None
    forward_from_message_id: int = None
    forward_signature: str = None
    forward_sender_name: str = None
    forward_date: int = None
    reply_to_message: 'Message' = None
    via_bot: User = None
    edit_date: int = None
    media_group_id: str = None
    author_signature: str = None
    # animation: Animation = None
    # audio: Audio = None
    # document: Document = None
    # photo: List[PhotoSize] = None
    # sticker: Sticker = None
    # video: Video = None
    # video_note: VideoNote = None
    # voice: Voice = None
    caption: str = None
    caption_entities: List[MessageEntity] = None
    # contact: Contact = None
    # dice: Dice = None
    # game: Game = None
    # poll: Poll = None
    # venue: Venue = None
    # location: Location = None
    new_chat_members: List[User] = None
    left_chat_member: User = None
    new_chat_title: str = None
    # new_chat_photo: List[PhotoSize] = None
    delete_chat_photo: bool = None
    group_chat_created: bool = None
    supergroup_chat_created: bool = None
    channel_chat_created: bool = None
    migrate_to_chat_id: int = None
    migrate_from_chat_id: int = None
    pinned_message: 'Message' = None
    # invoice: Invoice = None
    # successful_payment: SuccessfulPayment = None
    connected_website: str = None
    # passport_data: PassportData = None
    # reply_markup: InlineKeyboardMarkup = None

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

# https://core.telegram.org/bots/api#photosize


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
