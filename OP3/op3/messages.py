from datetime import datetime
from typing import NamedTuple, Any, Optional, Iterator

from abc import ABC, abstractmethod
from collections.abc import MutableSequence

from .encoders import ENCODERS, string_encode, default_encoder, datetime_encode, blob_encode

class Element(NamedTuple):
    value: Any
    tag: str
    @classmethod
    def from_pair(cls, value: Any, tag: Optional[str]=None) -> 'Element':
        if isinstance(value, Element):
            assert tag is None
            return value
        if isinstance(value, tuple):
            assert tag is None
            value, tag = value
        return cls(value, tag or default_encoder(value))
    def encode(self) -> bytes:
        return ENCODERS[self.tag](self.value)
    def __repr__(self):
        return f'Element({self.value!r}, tag={self.tag!r})'

class AbstractMessage(ABC, MutableSequence):
    address: str
    _items: list

    def clear(self):
        self._items.clear()

    def __len__(self):
        return len(self._items)

    def __getitem__(self, index):
        return self._items[index]

    def __delitem__(self, index):
        del self._items[index]

    @abstractmethod
    def _build_message(self) -> Iterator[bytes]:
        assert NotImplementedError # pragma: no cover

    def __bytes__(self):
        return b''.join(self._build_message())

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return other.address == self.address and other._items == self._items

class Message(AbstractMessage):
    def __init__(self, address: str, *args: Any) -> None:
        self.address = address
        self._items = []
        self.extend(args)

    def append(self, value: Any, *, tag: Optional[str]=None) -> None:
        self._items.append(Element.from_pair(value, tag))

    def insert(self, index: int, value: Any, *, tag: Optional[str]=None) -> None:
        self._items.insert(index, Element.from_pair(value, tag))

    def __setitem__(self, index, value):
        self._items[index] = Element.from_pair(value)

    def values(self) -> Iterator[Any]:
        for item in self._items:
            yield item.value

    def tags(self) -> Iterator[str]:
        for item in self._items:
            yield item.tag

    def _build_message(self) -> Iterator[bytes]:
        yield string_encode(self.address)
        yield string_encode(',' + ''.join(self.tags()))
        for item in self._items:
            yield item.encode()

    def __repr__(self):
        return f'Message({self.address!r}, {repr(self._items)[1:-1]})'

class Bundle(AbstractMessage):
    timetag: datetime
    def __init__(self, timetag: datetime, *args: Message) -> None:
        self.timetag = timetag
        self._items = []
        self.extend(args)

    @property
    def address(self):
        return '#bundle'

    def valid_to_insert(self, item: AbstractMessage):
        if not isinstance(item, AbstractMessage):
            return False
        if isinstance(item, Bundle):
            return item.timetag >= self.timetag
        return True

    def append(self, item: AbstractMessage) -> None:
        assert self.valid_to_insert(item)
        self._items.append(item)

    def insert(self, index: int, value: AbstractMessage) -> None:
        assert self.valid_to_insert(value)
        self._items.insert(index, value)

    def __setitem__(self, index, value):
        assert self.valid_to_insert(value)
        self._items[index] = value

    def _build_message(self) -> Iterator[bytes]:
        yield string_encode(self.address)
        yield datetime_encode(self.timetag)
        for item in self._items:
            yield blob_encode(bytes(item))

    def __eq__(self, other):
        return super().__eq__(other) and other.timetag == self.timetag 

    def __repr__(self):
        return f'Bundle({self.timetag!r}, {repr(self._items)[1:-1]})'
