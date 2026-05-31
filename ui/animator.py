from dataclasses import dataclass
from collections.abc import Callable

from utils.tiles    import Tile
from utils.vector   import Vector
from game           import board
from constants      import *

class Animator:
    ''' Class for bridging board coordinates to pixel coordinates '''
    def __init__(self, board: list[list[Tile]]):
        self.elapsed:  float      = 0
        self.progress: float      = 0
        self.active:   bool       = 0
        self.tiles:    list[Tile] = []
        self.set_tiles(board)

    def set_tiles(self, board: list[list[Tile]]) -> None:
        ''' Set up tile list for animation '''
        for tile in [tile for row in board for tile in row]:
            if tile.prev is None:
                tile.prev = tile.curr
            self.tiles.append(tile)

    def get_tiles(self) -> list[Tile]:
        ''' Return tiles with updated (animated) positions '''
        tiles = []
        for tile in self.tiles:
            # Does the reference break it???
            tile.pos = self._gridToPixel(*tile.prev).lerp(
                self._gridToPixel(*tile.curr),
                self._time_ease(self.progress)
            )
            tiles.append(tile)
        return tiles

    def update(self, dt: float) -> None:
        ''' Update animation timer & normalized progress '''
        self.elapsed  += dt
        self.progress  = self._time_clamp(self.elapsed / ANIMATION_DURATION)


    ########## ======== TIME MAPPING ======== ##########

    def _time_clamp(self, t: float, lower: float = 0, upper: float = 1) -> float:
        ''' Clamp t to a normalized value '''
        return min(upper, max(lower, t))

    def _time_ease(self, t: float) -> float:
        ''' Time-mapping function '''
        c1 = 1.1
        c3 = c1 + 1.0
        return 1.0 + c3 * ((t - 1.0) ** 3) + c1 * ((t - 1.0) ** 2)
    
    
    ########## ======= GRID TO PIXEL ======== ##########
    
    def _gridToPixel(self, rowIndex: int, colIndex: int) -> Vector:
        ''' Convert board coordinates to pixel coordinates '''
        x = CELL_PAD.w + (CELL_SIZE.w + CELL_PAD.w) * colIndex
        y = CELL_PAD.h + (CELL_SIZE.h + CELL_PAD.h) * rowIndex
        return Vector(x, y)
