from    random  import choice, random
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
        self.board     : list[list[Tile]]
        ''' Dict of all the directions with their respective functions '''
        self.move_func = {
            "left"  : self._move_left,
            "right" : self._move_right,
            "up"    : self._move_up,
            "down"  : self._move_down
        }
        self.tileSpawn : int
        self.score     : int
        self.reset(rows, cols, tileSpawn)


    ########## ===== MERGING & MOVEMENT ===== ##########

    def _compress_row(self, rowIndex: int) -> None:
        ''' Removes the zeros from a row '''
        self.board[rowIndex] = [tile for tile in self.board[rowIndex] if tile.value != 0]

    def _merge_row(self, rowIndex: int) -> None:
        '''
        Base logic for merging  
        Checks for adjacent pairs of the same value in the row, then merges them  
        Note: this method merges leftwards
        '''
        # Record positions & Spawn animation
        for tile in self.board[rowIndex]:
            tile.prev  = tile.curr # Record position
            tile.spawn = False # Stop spawn animations
        # Compress to remove null tiles
        self._compress_row(rowIndex)
        # Merge for each valid pair
        col = 0
        while col < len(self.board[rowIndex]):
            self._set_curr(rowIndex, col, (rowIndex, col))
            if col < len(self.board[rowIndex]) - 1:
                if self._get_value(rowIndex, col) == self._get_value(rowIndex, col+1): # Can merge
                    temp_mergedVal  = self.board[rowIndex][col].value * 2
                    # Update the primary tile
                    self._set_value(rowIndex, col, temp_mergedVal)
                    # Remove the secondary tile
                    self._set_value(rowIndex, col+1, 0) # Now redundant; will remove
                    # Update score
                    self.score     += temp_mergedVal
                    # Iterate
                    col += 2 # Skip over atrophied secondary tile
                else:
                    col += 1 # Iterate to next
            else:
                col += 1 # Iterate to next
        # Remove extra 0s, add 0s back to fill
        self._compress_row(rowIndex)
        self.board[rowIndex] += [Tile(curr=(rowIndex, c), prev=(rowIndex, c)) for c in range(len(self.board[rowIndex]), self.cols)]
        return

    def _merge_board(self):
        ''' Wrapper that performs _merge_row on the whole board '''
        for row in range(self.rows):
            self._merge_row(row)

    def _transpose(self) -> None:
        ''' Returns the board with the row and column swapped '''
        for row in self.board:
            for tile in row:
                tile.curr = (tile.curr[1], tile.curr[0])
                tile.prev = (tile.prev[1], tile.prev[0])
        self.board = [list(row) for row in zip(*self.board)] # Groups one index of each row in board

    def _reverse(self) -> None:
        ''' Reverses all the rows '''
        for row in self.board:
            for tile in row:
                tile.curr = (tile.curr[0], self.cols - tile.curr[1] - 1)
                tile.prev = (tile.prev[0], self.cols - tile.prev[1] - 1)
        self.board = [row[::-1] for row in self.board]

    def _move_left(self):
        ''' Performs a left move '''
        # tile.prev = tile.curr
        self._merge_board() # Since the move method shifts to the left, there is no variation
        # tile.curr = 

    def _move_right(self):
        ''' Performs a right move '''
        self._reverse()
        self._merge_board()
        self._reverse()

    def _move_up(self):
        ''' Performs an up move '''
        self._transpose()
        self._merge_board()
        self._transpose()

    def _move_down(self):
        ''' Performs a down move '''
        self._transpose()
        self._reverse()
        self._merge_board()
        self._reverse()
        self._transpose()

    def move(self, direction: str) -> bool: # Did a move happen?
        ''' Exposed enpoint for moving provided a direction '''
        oldBoard = copy.deepcopy(self.board)
        self.move_func[direction]()

        # Don't update if no move
        if self.board == oldBoard:
            return False
        
        # Add tile
        self._spawn_tile(self.tileSpawn)
        return True


    ########## ===== TILE MODIFICATION ====== ##########

    def _get_tile(self, row: int, col: int) -> Tile:
        ''' Gets the tile at a specific index '''
        return self.board[row][col]
    
    def _get_value(self, row: int, col: int) -> int:
        ''' Gets the tile at a specific index '''
        return self.board[row][col].value
    
    def _get_curr(self, row: int, col: int) -> tuple[int, int]:
        ''' Get the current tile position tile at a specific index '''
        return self.board[row][col].curr
    
    def _get_prev(self, row: int, col: int) -> tuple[int, int]:
        ''' Gets the previous tile position at a specific index '''
        return self.board[row][col].prev

    def _get_emptyCells(self) -> list[tuple[int, int]]:
        ''' Returns all the cells that has no numbers in it '''
        return [(r, c) for r in range(self.rows) for c in range(self.cols) if self.board[r][c].value == 0]

    def _set_value(self, row: int, col: int, val: int) -> None:
        ''' Sets the value of a tile given the index '''
        self.board[row][col].value = val
    
    def _set_curr(self, row: int, col: int, val: tuple[int, int]) -> None:
        ''' Set the current tile position tile at a specific index '''
        self.board[row][col].curr = val
    
    def _set_prev(self, row: int, col: int, val: tuple[int, int]) -> None:
        ''' Set the previous tile position tile at a specific index '''
        self.board[row][col].prev = val

    def _spawn_tile(self, num: int = 1) -> None:
        ''' Spawns new tiles at random empty spaces '''
        empty = self._get_emptyCells()
        for _ in range(num):
            if not empty: return # Break if no empty
            randomTile = choice(empty)
            val = 4 if random() < 0.1 else 2
            self._set_value(*randomTile, val)
            empty.remove(randomTile)


    ########## ========= WIN & LOSS ========= ##########

    def hasLegalMove(self) -> bool:
        ''' Checks if any moves are possible without altering the board '''
        for r in range(self.rows):
            for c in range(self.cols):
                # 1. If there's an empty space, a move is always possible
                if self.board[r][c].value == 0:
                    return True
                
                # 2. Check horizontal neighbor (to the right)
                if c < self.cols - 1 and self.board[r][c].value == self.board[r][c + 1].value:
                    return True
                    
                # 3. Check vertical neighbor (below)
                if r < self.rows - 1 and self.board[r][c].value == self.board[r + 1][c].value:
                    return True
                    
        # If the loop finishes and found no zeros and no matches, the player is locked out
        return False

    def hasWon(self) -> bool:
        ''' Check if the user has won '''
        return any(
            self._get_tile(r, c) == WIN_TILE
            for r in range(self.rows)
            for c in range(self.cols)
        )
    
    def reset(self, rows: int = 4, cols: int = 4, tileSpawn: int = 1) -> None:
        ''' Reverts the game state to inital state and clears the board '''
        self.rows      = rows
        self.cols      = cols
        self.board     = [[Tile(curr=(r, c)) for c in range(self.cols)] for r in range(self.rows)]
        self.tileSpawn = tileSpawn
        self.score     = 0
        # Add starting tiles
        self._spawn_tile(2)


    ########## =========== DEBUG ============ ##########

    def _printBoard(self) -> None:
        ''' Debug function for printing '''
        buffer = []
        for row in self.board:
            buffer.append(f"{" ".join(map(str, [tile.value for tile in row]))}")
        rowLen = len(buffer[0])
        print('┌', '─' * (rowLen + 2), '┐', sep='')
        for row in buffer: print(f"│ {row} │")
        print('└', '─' * (rowLen + 2), '┘', sep='')