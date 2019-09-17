from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class RGBA:
    red: int
    green: int
    blue: int
    alpha: int

@dataclass(frozen=True)
class MIDIMessage:
    port_id: int
    status: int
    data1: int
    data2: int

class ASAP(datetime):
    pass # FIXME: ensure relation to datetime.now()
    def __eq__(self, other):
        return True
    def __repr__(self):
        return 'ASAP.now()'