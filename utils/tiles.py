from dataclasses import dataclass

@dataclass
class Tile():
    value:  int
    cur:    tuple[int, int]
    next:   tuple[int, int]
    pos:    tuple[float, float]
    merged: bool