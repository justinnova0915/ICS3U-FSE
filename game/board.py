from    random  import choice, random
from    functools import wraps
import  copy

from    constants import *
from    utils.tiles import Tile

class Board:
    ''' Class for the game board '''

    def __init__(self, rows: int = 4, cols: int = 4, tileSpawn: int = 1) -> None:
        '''
        Initialize the Board object  
        Customization is supported. Default size 4x4, +1 tile / move
        '''
        self.rows      : int        = rows      # Number of rows
        self.cols      : int        = cols      # Number of columns
        self.board     : list[Tile] = []        # List of non-null tiles

        self.moved     : bool       = False     # Bool to check if spawned
        # Dict of all the directions with their respective movements
        self.move_dir = {"left": (0, -1), "right": (0, 1), "up": (-1, 0), "down": (1, 0)}

        self.tileSpawn : int        = tileSpawn # Number of tiles to spawn
        self.score     : int        = 0         # Total score
        self.moves     : int        = 0         # Number of moves made
        self.spawn_tile(num=2, addPoints=False)


    ########## ===== MERGING & MOVEMENT ===== ##########

    def _sortBoard(self, direction: str):
        
        match direction:
            case "left":
                self.board.sort(key=lambda tile: tile.curr[1])
            case "right":
                self.board.sort(key=lambda tile: tile.curr[1], reverse=True)
            case "up":
                self.board.sort(key=lambda tile: tile.curr[0])
            case "down":
                self.board.sort(key=lambda tile: tile.curr[0], reverse=True)
            
    def _searchBoard(self, index: tuple[int, int]) -> Tile | None:
        for tile in self.board:
            if tile.curr == index:
                return tile
        return None

    def _moveBoard(self, direction: str) -> None:
        '''
        Base logic for merging  
        Checks for adjacent pairs of the same value in the row, then merges them  
        Note: this method merges leftwards
        '''
        for tile in self.board:
            tile.merging = False

        self._sortBoard(direction)
        self.moved = False

        # Loop through each tile
        for tile in self.board:
            # Record the pos now as prev before moving
            if tile.prev == (-1, -1) and tile.merging:
                break
            tile.prev = tile.curr

            while True:
                # slide one spot
                r, c = tile.curr
                dr, dc = self.move_dir[direction]
                next_r, next_c = r + dr, c + dc
                # check if the coord is even in range (hit the bounds)
                if 0 <= next_r < self.rows and 0 <= next_c < self.cols:
                    # See if there is already a tile there
                    adj = self._searchBoard((next_r, next_c))
                    # if there is
                    if adj:
                        # 1. Already merged in this step, can;t merge again
                        if adj.merging:
                            break
                        # 2. check if its a blocking tile
                        elif adj.value != tile.value:
                            break
                        # 3. check if a merge can happen
                        elif adj.value == tile.value:
                            # if so, update the value and pos
                            adj.merging = True
                            tile.merging = True
                            tile.curr = (next_r, next_c)
                            self.board.append(Tile(
                                (next_r, next_c),
                                value=tile.value*2,
                                merging=True
                            ))
                            self.moved = True
                            self.score += tile.value*2
                            self.moves += 1
                            break
                    # if is none, then its an empty spot. move into it
                    else:
                        tile.curr = (next_r, next_c)
                        self.moved = True
                        self.moves += 1

                else:
                    break


    def move(self, direction: str) -> None:
        ''' Exposed endpoint for moving provided a direction '''
        oldBoard = copy.deepcopy(self.board)
        self._moveBoard(direction)

        # Don't update if no move
        if self.moved:
            return True
        return False
    
    def cleanup(self):
        self.board = [tile for tile in self.board if not(tile.merging and tile.prev != (-1, -1))]


    ########## ============ TILE ============ ##########
    
    def _get_tile(self, row: int, col: int) -> Tile:
        ''' Gets the tile at a specific index '''
        return self._searchBoard((row, col))
    
    def _get_value(self, row: int, col: int) -> int:
        ''' Gets the tile at a specific index '''
        return self._get_tile(row, col).value
    
    def _get_curr(self, row: int, col: int) -> tuple[int, int]:
        ''' Get the current tile position tile at a specific index '''
        return self._get_tile(row, col).curr
    
    def _get_prev(self, row: int, col: int) -> tuple[int, int]:
        ''' Gets the previous tile position at a specific index '''
        return self._get_tile(row, col).prev
    
    def _set_tile(self, row: int, col: int, val: int) -> None:
        '''
        Sets a new tile object at the given index  
        Note: Removes the previous tile object
        '''
        self.board.append(
            Tile(
                curr=(row, col),
                value=val
            )
        )


    ########## ========= SPAWN TILE ========= ##########

    def _get_emptyTiles(self) -> list[tuple[int, int]]:
        ''' Returns all the cells that has no numbers in it '''
        return [(r, c) for r in range(self.rows) for c in range(self.cols) if self._searchBoard((r, c)) == None]

    def spawn_tile(self, num: int = 1, addPoints: bool = True) -> None:
        ''' Spawns new tiles at random empty spaces '''
        empty = self._get_emptyTiles()
        for _ in range(num):
            if not empty: return # Stop if no empty tiles
            randomIndex = choice(empty)
            val = 4 if random() < 0.1 else 2
            # Add new tile
            self._set_tile(*randomIndex, val)
            # Add score of new tile
            if addPoints:
                self.score += val
            # Remove index from empty indexes
            empty.remove(randomIndex)


    ########## ======= WIN LOSS CHECK ======= ##########

    def hasLegalMove(self) -> bool:
        ''' Checks if any moves are possible without altering the board '''

        if len(self.board) < (self.rows * self.cols):
            return True
        
        tile_map = {tile.curr: tile.value for tile in self.board}

        for (r, c), value in tile_map.items():
            # Check right neighbor
            if c < self.cols - 1 and tile_map.get((r, c + 1)) == value:
                return True
                
            # Check bottom neighbor
            if r < self.rows - 1 and tile_map.get((r + 1, c)) == value:
                return True
        
        return False

    def hasWon(self) -> bool:
        ''' Check if the user has won '''
        for tile in self.board:
            if tile.value == WIN_TILE:
                return True
        return False                
    

    ########## ========== POWERUPS ========== ##########


    ########## =========== DEBUG ============ ##########

    def _get_boardValues(self) -> list[list[int]]:
        values = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        for r in range(self.rows):
            for c in range(self.cols):
                tile = self._searchBoard(r, c)
                if tile is not None:
                    values[r][c] = tile.value
        return values

    def _set_boardValues(self, values: list[list[int]]) -> None:
        self.board = [
            Tile((r, c), value=values[r][c])
            
            for r in range(len(values))
                for c in range(len(values[r]))
                    if values[r][c] != 0
        ]

    def _print_board(self) -> None:
        ''' Debug function for printing the flat-list board layout '''
        # 1. Create a fast coordinate lookup map: {(r, c): value}
        tile_map = {tile.curr: tile.value for tile in self.board}
        
        # 2. Build the text rows by scanning coordinates line by line
        buffer = []
        for r in range(self.rows):
            row_strings = []
            for c in range(self.cols):
                val = tile_map.get((r, c))
                # Print a dot or space if empty, otherwise stringify the value
                row_strings.append(str(val) if val else ".")
            buffer.append("  ".join(row_strings))
            
        # 3. Handle the box formatting based on the longest row length
        rowLen = max(len(row) for row in buffer) if buffer else 0
        print('┌', '─' * (rowLen + 2), '┐', sep='')
        for row in buffer: 
            # Left-align the text to keep the box borders perfectly aligned
            print(f"│ {row:<{rowLen}} │")
        print('└', '─' * (rowLen + 2), '┘', sep='')