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
        self.rows      : int
        self.cols      : int
        self.board     : list[Tile]
        self.moves     : int
        ''' Dict of all the directions with their respective functions '''
        self.move_dir = {
            "left": (0, -1),
            "right": (0, 1),
            "up": (-1, 0),
            "down": (1, 0)
        }
        self.tileSpawn : int
        self.score     : int
        self.moved     : bool
        self.reset(rows, cols, tileSpawn)
    
    def reset(self, rows: int = 4, cols: int = 4, tileSpawn: int = 1) -> None:
        ''' Reverts the game state to inital state and clears the board '''
        self.rows      = rows
        self.cols      = cols
        self.board     = []
        self.tileSpawn = tileSpawn
        self.score     = 0
        self.moved     = False
        self.moves     = 0
        # Add starting tiles
        self.spawn_tile(2)


    ########## ===== MERGING & MOVEMENT ===== ##########

    def _sort_board(self, direction: str):
        
        match direction:
            case "left":
                self.board.sort(key=lambda tile: tile.curr[1])
            case "right":
                self.board.sort(key=lambda tile: tile.curr[1], reverse=True)
            case "up":
                self.board.sort(key=lambda tile: tile.curr[0])
            case "down":
                self.board.sort(key=lambda tile: tile.curr[0], reverse=True)
            
    def _search_board(self, index: tuple[int, int]):
        return next((t for t in self.board if t.curr == index and t.value > 0), None)

    def _move_board(self, direction: str) -> None:
        '''
        Base logic for merging  
        Checks for adjacent pairs of the same value in the row, then merges them  
        Note: this method merges leftwards
        '''
        for tile in self.board:
            tile.merging = False

        self._sort_board(direction)
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
                    adj = self._search_board((next_r, next_c))
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


    def tryMove(self, direction: str) -> bool: # Did a move happen?
        ''' Exposed endpoint for moving provided a direction '''
        oldBoard = copy.deepcopy(self.board)
        self._move_board(direction)

        # Don't update if no move
        if self.moved:
            return True
        return False
    
    def cleanup(self):
        self.board = [tile for tile in self.board if not(tile.merging and tile.prev != (-1, -1))]


    ########## ============ TILE ============ ##########
    
    def _get_tile(self, row: int, col: int) -> Tile:
        ''' Gets the tile at a specific index '''
        return self._search_board((row, col))
    
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

    def _get_empty_tiles(self) -> list[tuple[int, int]]:
        ''' Returns all the cells that has no numbers in it '''
        return [(r, c) for r in range(self.rows) for c in range(self.cols) if self._search_board((r, c)) == None]

    def spawn_tile(self, num: int = 1) -> None:
        ''' Spawns new tiles at random empty spaces '''
        empty = self._get_empty_tiles()
        for _ in range(num):
            if not empty: return # Stop if no empty tiles
            randomIndex = choice(empty)
            val = 4 if random() < 0.1 else 2
            # Add new tile
            self._set_tile(*randomIndex, val)
            # Remove index from empty indexes
            empty.remove(randomIndex)


    ########## ======= WIN LOSS CHECK ======= ##########

    def _get_board_values(self, board: list[list[Tile]] | None = None) -> list[list[int]]:
        if board is None:
            return [[tile.value for tile in row] for row in self.board]
        else:
            return [[tile.value for tile in row] for row in board]

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
    
    ########## =========== DEBUG ============ ##########

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