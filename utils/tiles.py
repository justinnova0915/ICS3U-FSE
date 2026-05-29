from dataclasses import dataclass

@dataclass
class TileMove():
    value: int
    start: tuple[int, int]
    end: tuple[int, int]
    merged: bool
    

@dataclass
class TileDraw():
    value: int
    pos: tuple[float, float]