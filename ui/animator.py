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
        self.tiles: list[list[Tile]] = []

    def load_queue(self, board: list[list[Tile]]):
        for tile in board:
            self.tiles.append(tile)
    
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

    def update(self, dt: float) -> list[list[Tile]]:
        self.elapsed += dt
        progress = min(self.elapsed/ANIM_DURATION, 1.0)
        board = []

        if progress == 1.0:
            self.tiles = []
        
        for r in self.tiles:
            for tween in r:
                tween.pos = self._lerp(tween.curr, tween.p, progress)
                board.append(tween)
        
        return board

    def get_active(self) -> list[Tile]:
        return self.active