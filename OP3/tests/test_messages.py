from datetime import datetime
import math
import pytest

from op3 import Message, Element, Bundle, parse, ASAP, MIDIMessage, RGBA
from op3.messages import AbstractMessage

def assert_roundtrips(msg: AbstractMessage) -> None:
    assert parse(bytes(msg)) == msg

def test_empty_message_roundtrips():
    assert_roundtrips(Message('/my/test'))

def test_none_roundtrips():
    assert_roundtrips(Message('/my/test', None))

def test_str_roundtrips():
    assert_roundtrips(Message('/my/test', "hello"))

def test_blob_roundtrips():
    assert_roundtrips(Message('/my/test', b"hello"))

def test_int32_roundtrips():
    assert_roundtrips(Message('/my/test', 10_000))

def test_int64_roundtrips():
    assert_roundtrips(Message('/my/test', Element(10_000, 'h')))

def test_bool_roundtrips():
    assert_roundtrips(Message('/my/test', True, False))

def test_datetime_roundtrips():
    assert_roundtrips(Message('/my/test', datetime(2019, 5, 2)))

def test_datetime_roundtrips2():
    assert_roundtrips(Message('/my/test', datetime(2019, 10, 2)))

def test_datetime_roundtrips3():
    assert_roundtrips(Message('/my/test', datetime(2019, 10, 2, 21, 9, 8)))

def test_float_roundtrips():
    assert_roundtrips(Message('/my/test', *[Element(x, tag='d') for x in (10.0, 0.5, 12345.6789, math.pi, math.inf, -math.inf)]))

def test_float32_roundtrips():
    assert_roundtrips(Message('/my/test', 10.0, 0.5, math.inf, -math.inf))
    # FIXME: write tests for floats that don't survive float64 -> float32 -> float64 roundtrip

def test_midi_roundtrips():
    assert_roundtrips(Message('/my/test', MIDIMessage(1, 2, 3, 4)))

def test_rgba_roundtrips():
    assert_roundtrips(Message('/my/test', RGBA(255, 128, 0, 100)))

def test_character_roundtrips():
    assert_roundtrips(Message('/my/test', Element(ord('O'), 'c')))
    assert parse(bytes(Message('/my/test', Element('O', 'c')))) == Message('/my/test', Element(ord('O'), 'c')) 

def test_auto_float_types():
    assert Element.from_pair(math.pi).tag == 'f'
    assert Element.from_pair(1e300).tag == 'd'

def test_wrong_type():
    with pytest.raises(TypeError):
        print(Element.from_pair(object()))

def test_adding_tuples():
    a = Message('/my/test', 1)

    b = Message('/my/test')
    b.append(1, tag='i')

    c = Message('/my/test')
    c.append((1, 'i'))

    assert a == b == c

def test_insert():
    a = Message('/my/test', 10, 20)
    b = Message('/my/test', 20)
    b.insert(0, 10)
    assert a == b

def test_getitem():
    assert Message('/my/test', 'a', 'b', 'c')[2] == Element.from_pair('c')

def test_setitem():
    msg = Message('/my/test', 'a', 'b', 'c')
    msg[2] = 100
    assert msg == Message('/my/test', 'a', 'b', 100)

def test_delitem():
    msg = Message('/my/test', 'a', 'b', 'c')
    del msg[1]
    assert msg == Message('/my/test', 'a', 'c')

def test_insert_bundle():
    a = Bundle(ASAP.now(), Message('/my/test'), Message('/hello'))
    b = Bundle(ASAP.now(), Message('/hello'))
    b.insert(0, Message('/my/test'))
    assert a == b

def test_getitem_bundle():
    assert Bundle(ASAP.now(), Message('/my/test'), Message('/my/test', 1), Message('/my/test', 2))[2] == Message('/my/test', 2)

def test_setitem_bundle():
    msg = Bundle(ASAP.now(), Message('/my/test'), Message('/my/test', 1), Message('/my/test', 2))
    msg[2] = Message('/oh/no', b'surprise')
    assert msg == Bundle(ASAP.now(), Message('/my/test'), Message('/my/test', 1), Message('/oh/no', b'surprise'))

def test_delitem_bundle():
    msg = Bundle(ASAP.now(), Message('/my/test'), Message('/my/test', 1), Message('/my/test', 2))
    del msg[1]
    assert msg == Bundle(ASAP.now(), Message('/my/test'), Message('/my/test', 2))

def test_clear():
    msg = Message('/my/test', 'a', 'b', 'c')
    assert len(msg) == 3
    msg.clear()
    assert len(msg) == 0

def test_asap():
    assert_roundtrips(Message('/my/test', ASAP.now()))

def test_bundle2():
    timetag = datetime(2019, 9, 17, 21, 49, 43, 677925)
    assert_roundtrips(Bundle(timetag, Message('/some/test', 1), Message('/some/test', 2, timetag)))

def test_bundle():
    assert_roundtrips(Bundle(ASAP.now(), Message('/my/test', 333, True), Message('/more/tests', "ok")))
    assert_roundtrips(Bundle(datetime(2019, 5, 2), Message('/my/test', 333, True), Message('/more/tests', "ok")))
    assert_roundtrips(Bundle(datetime.now(), Message('/my/test', 333, True), Message('/more/tests', "ok")))
    assert_roundtrips(Bundle(datetime.now(), Message('/my/test', 333, True), Bundle(datetime.now(), Message('/more/tests', "ok"))))

def assert_repr(s):
    assert repr(eval(s)) == s

def test_reprs():
    assert_repr("Element('hello', tag='s')")
    assert_repr("Message('/my', Element(1, tag='i'))")
    assert_repr("Bundle(ASAP.now(), Message('/my', Element(1, tag='i')))")

def test_values():
    assert list(Message('/my/test', 10, True, "Buffalo").values()) == [10, True, "Buffalo"]

def test_weird_stuff_in_bundle():
    with pytest.raises(AssertionError):
        Bundle(ASAP.now(), 'oh no')

def test_message_is_not_bundle():
    assert Message('#bundle') != Bundle(ASAP.now())