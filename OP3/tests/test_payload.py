from op3 import ASAP

def test_asap_repr():
    assert repr(ASAP.now()) == 'ASAP.now()'

def test_asap_eq():
    assert ASAP.now() == ASAP(1991, 11, 14)