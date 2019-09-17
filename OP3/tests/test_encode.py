from op3.encoders import string_encode, char_encode
import pytest

def test_string_contains_nul():
    with pytest.raises(ValueError):
        string_encode('hell\x00o')

def test_char_type():
    with pytest.raises(TypeError):
        char_encode(b'x')
