from typing import Tuple, Any, Dict, Callable
from struct import Struct
from datetime import datetime, timedelta
import numbers

from .payload_types import RGBA, MIDIMessage, ASAP

INT32_MAX = (1 << 31) - 1
INT32_MIN = -(1 << 31)
NTP_EPOCH = datetime(1900, 1, 1)
NTP_DENOM = 1 << 31
ONE_SECOND = timedelta(seconds=1)

int32 = Struct('>i')
int64 = Struct('>q')
float32 = Struct('>f')
float64 = Struct('>d')
twoints = Struct('>II')
fourints = Struct('>4i')

def _nul_pad(s: bytes) -> bytes:
    return s + b'\0' * (4 - len(s) % 4)

def string_encode(s: str) -> bytes:
    if '\0' in s:
        raise ValueError('OSC-strings cannot contain NUL characters')
    return _nul_pad(s.encode('ascii'))

def blob_encode(b: bytes) -> bytes:
    return int32.pack(len(b)) + _nul_pad(b)

def null_encode(value: Any) -> bytes:
    return b''

def datetime_encode(value: datetime) -> bytes:
    if isinstance(value, ASAP):
        s, us = 0, 1
    else:
        s, us_ = divmod(value - NTP_EPOCH, ONE_SECOND)
        us = int(us_.microseconds * NTP_DENOM / 1000_000)
    return twoints.pack(s, us)

def char_encode(value: Any) -> bytes:
    if isinstance(value, str):
        assert len(value) == 1
        return int32.pack(ord(value))
    elif isinstance(value, int):
        return int32.pack(value)
    raise TypeError(f'char can only be str or int, not {type(value)}')


def rgba_encode(value: RGBA) -> bytes:
    return fourints.pack(value.red, value.green, value.blue, value.alpha)

def midi_encode(value: MIDIMessage) -> bytes:
    return fourints.pack(value.port_id, value.status, value.data1, value.data2)


ENCODERS: Dict[str, Callable[[Any], bytes]] = {
    'i': int32.pack,
    'f': float32.pack,
    's': string_encode,
    'b': blob_encode,
    'h': int64.pack,
    't': datetime_encode,
    'd': float64.pack,
    'S': string_encode,
    'c': char_encode,
    'r': rgba_encode,
    'm': midi_encode,
    'T': null_encode,
    'F': null_encode,
    'N': null_encode,
    'I': null_encode,
}

def default_encoder(value: Any) -> str:
    if value is None:
        return 'N'
    elif isinstance(value, bool):
        return 'T' if value else 'F'
    elif isinstance(value, numbers.Integral):
        return 'i' if INT32_MIN <= value <= INT32_MAX else 'h'
    elif isinstance(value, numbers.Real):
        try:
            float32.pack(value)
        except ArithmeticError:
            return 'd'
        return 'f'
    elif isinstance(value, str):
        return 's'
    elif isinstance(value, bytes):
        return 'b'
    elif isinstance(value, RGBA):
        return 'r'
    elif isinstance(value, MIDIMessage):
        return 'm'
    elif isinstance(value, datetime):
        return 't'
    raise TypeError(f'cannot encode type {type(value)}, if possible, supply a tag')