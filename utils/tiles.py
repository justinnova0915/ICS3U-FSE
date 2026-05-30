from dataclasses import dataclass

from .vector     import Vector

@dataclass
class Tile():
    curr:   tuple[int, int]
    prev:   tuple[int, int] | None = None
    pos:    Vector          | None = None
    value:  int                    = 0
    merged: bool                   = False

    def __repr__(self):
        return f"Tile({self.value})"