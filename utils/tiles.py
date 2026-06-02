from dataclasses import dataclass

from .vector     import Vector

@dataclass
class Tile():
    curr:   tuple[int, int]
    prev:   tuple[int, int] = (0, 0)
    pos:    Vector   | None = None # get molested
    value:  int             = 0
    merged: bool            = False
    spawn:  bool            = True

    def __repr__(self):
        return f"Tile({self.value})"