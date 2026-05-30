from dataclasses import dataclass

@dataclass
class Tile():
    value:  int                         = 0
    curr:   tuple[int, int]
    prev:   tuple[int, int]     | None  = None
    pos:    tuple[float, float] | None  = None
    merged: bool                        = False