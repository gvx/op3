from typing import Tuple

from .decoders import DECODERS, string_decode, datetime_decode, blob_decode
from .messages import AbstractMessage, Bundle, Message, Element

def expect_bundle(view: memoryview) -> Tuple[memoryview, Bundle]:
    view, timetag = datetime_decode(view)
    bundle = Bundle(timetag)
    while view:
        view, blob = blob_decode(view)
        _, submessage = expect_message_or_bundle(memoryview(blob))
        bundle.append(submessage)
    return view, bundle

def expect_message(address: str, view: memoryview) -> Tuple[memoryview, Message]:
    view, tags = string_decode(view)
    assert tags.startswith(',')
    message = Message(address)
    for tag in tags[1:]:
        view, value = DECODERS[tag](view)
        message.append(Element(value, tag))
    return view, message


def expect_message_or_bundle(view: memoryview) -> Tuple[memoryview, AbstractMessage]:
    view, address = string_decode(view)
    if address == '#bundle':
        return expect_bundle(view)
    return expect_message(address, view)

def parse(source: bytes) -> AbstractMessage:
    return expect_message_or_bundle(memoryview(source))[1]
