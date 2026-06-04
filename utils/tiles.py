from dataclasses import dataclass

from constants      import *
from utils.vector   import Vector

@dataclass
class Tile():
    curr:   tuple[int, int]
    prev:   tuple[int, int] = (-1, -1)
    pos:    Vector | None   = None
    value:  int             = 0
    merged: bool            = False
    size:   Vector | None   = None

    def __repr__(self):
        return f"Tile({self.value})"