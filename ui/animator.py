from dataclasses import dataclass
from collections.abc import Callable

from utils.tiles import Tile
from game import board
from utils import vector
from constants import *

class Animator:
    def __init__(self):
        self.elapsed = 0
        self.progress = 0
        self.active = []

    def load_queue(self, moved: list[Tile]):
        for tile in moved:

            start = (float(self._gridToPixel(tile.start[0])), 
                    float(self._gridToPixel(tile.start[1])))
            end   = (float(self._gridToPixel(tile.end[0])), 
                    float(self._gridToPixel(tile.end[1])))
            
            self.active.append(Tile(
                value   = tile.value,
                curr    = start,
                prev    = end,
                merged  = tile.merged
            ))
    


    def update(self, dt: float):
        self.elapsed += dt
        progress = min(self.elapsed/ANIM_DURATION, 1.0)
        result = []

        if progress == 1.0:
            self.active = []
        
        for tile in self.active:
            lerpedPos = self._lerp(tile.sPos, tile.ePos, progress)
            result.append(Tile(
                value = tile.value,
                pos   = lerpedPos
            ))

    def get_active(self) -> list[Tile]:
        return self.active
    

    def _gridToPixel(self, rowIndex: int, colIndex: int) -> Coord:
        ''' Converts a grid coordinate to a pixel coordinate '''
        x = CELL_PAD.w + (CELL_SIZE.w + CELL_PAD.w) * colIndex
        y = CELL_PAD.h + (CELL_SIZE.h + CELL_PAD.h) * rowIndex
        return Coord(x, y)
    
    def _lerp(self, start: tuple[float, float], end: tuple[float, float], t: float) -> float:
        return tuple(
            start[0] + (end[0]-start[0]) * self._ease(t),
            start[1] + (end[1]-start[1]) * self._ease(t)
        )
    
    def _ease(progress: float) -> float:
        c1 = 1.1
        c3 = c1 + 1.0
        return 1.0 + c3 * ((progress - 1.0) ** 3) + c1 * ((progress - 1.0) ** 2)