from dataclasses import dataclass

from constants      import *
from utils.vector   import Vector

@dataclass
class Tile():
    curr:    tuple[int, int]
    prev:    tuple[int, int] = (-1, -1)
    pos:     Vector | None   = None
    size:    Vector | None   = None
    value:   int             = 0
    merging: bool            = False

    def __repr__(self):
        return f"Tile({self.value})"