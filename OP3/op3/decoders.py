from typing import Tuple, Any, Dict, Callable
import math
from datetime import datetime
from functools import partial

from .encoders import int32, int64, float32, float64, twoints, fourints, NTP_EPOCH, ONE_SECOND, NTP_DENOM
from .payload_types import RGBA, MIDIMessage, ASAP

def pad_index(index: int) -> int:
    return math.ceil(index / 4 + .25) * 4

def string_decode(view: memoryview) -> Tuple[memoryview, str]:
    for i, c in enumerate(view):
        if c == 0:
            return view[pad_index(i):], str(view[:i], 'ascii')
    else:
        raise ValueError("cannot decode string: no NUL terminator")

def blob_decode(view: memoryview) -> Tuple[memoryview, bytes]:
    view, length = int32_decode(view)
    return view[pad_index(length):], bytes(view[:length])

def null_decode(value: Any, view: memoryview) -> Tuple[memoryview, Any]:
    return view, value

def int32_decode(view: memoryview) -> Tuple[memoryview, int]:
    return view[int32.size:], int32.unpack_from(view)[0]

def int64_decode(view: memoryview) -> Tuple[memoryview, int]:
    return view[int64.size:], int64.unpack_from(view)[0]

def float32_decode(view: memoryview) -> Tuple[memoryview, float]:
    return view[float32.size:], float32.unpack_from(view)[0]

def float64_decode(view: memoryview) -> Tuple[memoryview, float]:
    return view[float64.size:], float64.unpack_from(view)[0]

def rgba_decode(view: memoryview) -> Tuple[memoryview, RGBA]:
    return view[fourints.size:], RGBA(*fourints.unpack_from(view))

def midi_decode(view: memoryview) -> Tuple[memoryview, MIDIMessage]:
    return view[fourints.size:], MIDIMessage(*fourints.unpack_from(view))

def datetime_decode(view: memoryview) -> Tuple[memoryview, datetime]:
    s, us = twoints.unpack_from(view)
    if s == 0 and us == 1:
        return view[twoints.size:], ASAP.now()
    return view[twoints.size:], NTP_EPOCH + ONE_SECOND * (s + us / NTP_DENOM)

DECODERS: Dict[str, Callable[[memoryview], Tuple[memoryview, Any]]] = {
    'i': int32_decode,
    'f': float32_decode,
    's': string_decode,
    'b': blob_decode,
    'h': int64_decode,
    't': datetime_decode,
    'd': float64_decode,
    'S': string_decode,
    'c': int32_decode,
    'r': rgba_decode,
    'm': midi_decode,
    'T': partial(null_decode, True),
    'F': partial(null_decode, False),
    'N': partial(null_decode, None),
    'I': partial(null_decode, math.inf),
}
