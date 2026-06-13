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


    ########## ===== CONFIG & RETRIEVAL ===== ##########

    def startAnimation(self, board: list[Tile]) -> None:
        self.active  = True
        self.tiles   = []
        self.elapsed = 0
        self._set_tiles(board)

    def _set_tiles(self, board: list[Tile]) -> None:
        ''' Set up tile list for animation '''
        for tile in board: 
            tile.pos = Vector(self._gridToPixel(*tile.curr))
            tile.size = Vector(CELL_SIZE)
            self.tiles.append(tile)
    
    def get_animatedTiles(self) -> list[Tile]:
        return self.tiles


    ########## =========== UPDATE =========== ##########

    def update(self, dt: float) -> list[Tile]:
        ''' Update animation timer & normalized progress '''
        if not self.active:
            return self.tiles
        self.elapsed  += dt
        self.progress  = self._clamp(self.elapsed / ANIMATION_DURATION)

        if self.progress == 1:
            self.tiles = [tile for tile in self.tiles if not(tile.merging and tile.prev != (-1, -1))]
            self.active = False
        
        for tile in self.tiles:
            self._animationFunction(tile)(tile)
            
        return self.tiles
    

    ########## ========= ANIMATIONS ========= ##########

    def _animationFunction(self, tile: Tile) -> Callable:
        if tile.prev == (-1, -1):
            return self._animation_spawn
        else:
            return self._animation_move

    def _animation_spawn(self, tile: Tile) -> None:
        tile.size = Vector((0, 0)).lerp(
            (CELL_SIZE), 
            self._timeMap_spawn(self.progress)
        )
        tile.pos = Vector(self._gridToPixel(*tile.curr)+(CELL_SIZE[0]/2, CELL_SIZE[1]/2)).lerp(
            self._gridToPixel(*tile.curr),
            self._timeMap_spawn(self.progress)
        )

    def _animation_move(self, tile: Tile) -> None:
        tile.pos = Vector(self._gridToPixel(*tile.prev)).lerp(
            self._gridToPixel(*tile.curr),
            self._timeMap_move(self.progress)
        )


    ########## ======== TIME MAPPING ======== ##########

    def _clamp(self, t: float, lower: float = 0, upper: float = 1) -> float:
        ''' Clamp t to a normalized value '''
        return min(upper, max(lower, t))
    
    def _timeMap_spawn(self, t: float) -> float:
        ''' Time-mapping function for tile spawning '''
        c1 = 2
        c3 = c1 + 1.0
        return 1.0 + c3 * ((t - 1.0) ** 3) + c1 * ((t - 1.0) ** 2)

    def _timeMap_move(self, t: float) -> float:
        ''' Time-mapping function for tile moving '''
        c1 = 0.5
        c3 = c1 + 1.0
        return 1.0 + c3 * ((t - 1.0) ** 3) + c1 * ((t - 1.0) ** 2)
    
    
    ########## ======= MISCELLANEOUS ======== ##########

    def _gridToPixel(self, rowIndex: int, colIndex: int) -> Vector:
        ''' Convert board coordinates to pixel coordinates '''
        x = CELL_PAD.w + (CELL_SIZE.w + CELL_PAD.w) * colIndex
        y = CELL_PAD.h + (CELL_SIZE.h + CELL_PAD.h) * rowIndex
        return Vector(x, y)