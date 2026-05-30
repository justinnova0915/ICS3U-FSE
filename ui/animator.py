from dataclasses import dataclass
from collections.abc import Callable

from utils.tiles import TileDraw, TileMove
from game import board
from utils import vector
from constants import *

class Animator:
    def __init__(self):
        self.elapsed = 0
        self.progress = 0
        self.active = []

    def load_queue(self, moved: list[TileMove]):
        for tile in moved:

            start = (float(self._gridToPixel(tile.start[0])), 
                    float(self._gridToPixel(tile.start[1])))
            end   = (float(self._gridToPixel(tile.end[0])), 
                    float(self._gridToPixel(tile.end[1])))
            
            self.active.append(Tween(
                tile.value,
                start,
                end,
                tile.merged
            ))
    
    def _ease(progress: float) -> float:
        c1 = 1.1
        c3 = c1 + 1.0
        return 1.0 + c3 * ((progress - 1.0) ** 3) + c1 * ((progress - 1.0) ** 2)

    def _lerp(self, start: tuple[float, float], end: tuple[float, float], progess: float) -> float:
        eased_progress = self._ease(progess)
        return tuple(
            start[0] + (end[0]-start[0])*eased_progress,
            start[1] + (end[1]-start[1])*eased_progress
        )

    def update(self, dt: float):
        self.elapsed += dt
        progress = min(self.elapsed/ANIM_DURATION, 1.0)
        result = []

        if progress == 1.0:
            self.active = []
        
        for tween in self.active:
            lerpedPos = self._lerp(tween.sPos, tween.ePos, progress)
            result.append(TileDraw(
                tween.value,
                lerpedPos
            ))

    def get_active(self) -> list[TileMove]:
        return self.active