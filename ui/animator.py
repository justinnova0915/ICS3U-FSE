from dataclasses import dataclass
from collections.abc import Callable
from functools import wraps

from utils.tiles    import Tile
from utils.vector   import Vector
from game           import board
from constants      import *

class Animator:
    ''' Class for bridging board coordinates to pixel coordinates '''
    def __init__(self, board: list[list[Tile]]):
        self.elapsed:  float      = 0
        self.progress: float      = 0
        self.active:   bool       = False
        self.tiles:    list[Tile] = []
        self._set_tiles(board)


    ########## =========== SET UP =========== ##########

    def load_tiles(self, board: list[list[Tile]]) -> None:
        self.active  = True
        self.tiles   = []
        self.elapsed = 0
        self._set_tiles(board)

    def _set_tiles(self, board: list[list[Tile]]) -> None:
        ''' Set up tile list for animation '''
        for row in board: 
            for tile in row:
                tile.pos = Vector(self._gridToPixel(*tile.curr))
                tile.size = CELL_SIZE
                self.tiles.append(tile)
    
    def get_animatedTiles(self) -> list[Tile]:
        return self.tiles


    ########## =========== UPDATE =========== ##########

    def update(self, dt: float) -> list[Tile]:
        ''' Update animation timer & normalized progress '''
        if not self.active:
            return self.tiles
        self.elapsed  += dt
        self.progress  = self._time_clamp(self.elapsed / ANIMATION_DURATION)

        if self.progress == 1:
            self.active = False
        
        for tile in self.tiles:
            if tile.prev == (-1, -1):
                self.lerp_spawn(tile)
            else:
                self.lerp(tile)
        return self.tiles
    

    ########## ========= ANIMATIONS ========= ##########

    def lerp_spawn(self, tile: Tile):
        tile.size = Vector((0, 0)).lerp(
            (CELL_SIZE), 
            self._time_ease(self.progress)
        )
        tile.pos = Vector(self._gridToPixel(*tile.curr)+(CELL_SIZE[0]/2, CELL_SIZE[1]/2)).lerp(
            self._gridToPixel(*tile.curr),
            self._time_ease(self.progress)
        )

    def lerp(self, tile: Tile):
        tile.pos = Vector(self._gridToPixel(*tile.prev)).lerp(
            self._gridToPixel(*tile.curr),
            self._time_ease(self.progress)
        )

    ########## ======== TIME MAPPING ======== ##########

    def _time_clamp(self, t: float, lower: float = 0, upper: float = 1) -> float:
        ''' Clamp t to a normalized value '''
        return min(upper, max(lower, t))

    def _time_ease(self, t: float) -> float:
        ''' Time-mapping function '''
        c1 = 0.5
        c3 = c1 + 1.0
        return 1.0 + c3 * ((t - 1.0) ** 3) + c1 * ((t - 1.0) ** 2)
    
    
    ########## ======= MISCELLANEOUS ======== ##########

    def _gridToPixel(self, rowIndex: int, colIndex: int) -> Vector:
        ''' Convert board coordinates to pixel coordinates '''
        x = CELL_PAD.w + (CELL_SIZE.w + CELL_PAD.w) * colIndex
        y = CELL_PAD.h + (CELL_SIZE.h + CELL_PAD.h) * rowIndex
        return Vector(x, y)