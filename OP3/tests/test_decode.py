from op3.decoders import string_decode
import pytest

def test_string_missing_nul():
    with pytest.raises(ValueError):
        string_decode(b'abcd')
