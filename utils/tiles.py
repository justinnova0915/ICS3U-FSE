from dataclasses import dataclass

@dataclass
class Tile():
    value:  int
    curr:   tuple[int, int]
    prev:   tuple[int, int]     | None
    pos:    tuple[float, float] | None
    merged: bool