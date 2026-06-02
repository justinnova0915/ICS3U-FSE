from dataclasses import dataclass

from .vector     import Vector

@dataclass
class Tile():
    curr:   tuple[int, int]
    prev:   tuple[int, int] = (-1, -1)
    pos:    Vector          = None
    value:  int             = 0
    merged: bool            = False
    size:   Vector          = None

    def __repr__(self):
        return f"Tile({self.value})"