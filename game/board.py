from    random  import choice, random
import  copy

from    constants   import *
from    utils.tiles import Tile

class Board:
    ''' Main class for the game board '''

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


    ########## ============ MISC ============ ##########
    
    def _gridToPixel(self, rowIndex: int, colIndex: int) -> Coord:
        ''' Converts a grid coordinate to a pixel coordinate '''
        x = CELL_PAD.w + (CELL_SIZE.w + CELL_PAD.w) * col
        y = CELL_PAD.h + (CELL_SIZE.h + CELL_PAD.h) * rowIndex
        return Coord(x, y) 


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
        points = 0
        self._compress_row(rowIndex)
        # Merge for each valid pair
        row = self.board[rowIndex]
        for i in range(len(row) - 1):
            currTile = row[i]
            nextTile = row[i+1]
            if currTile.value == nextTile.value:
                temp_mergedVal  = currTile * 2
                currTile  = temp_mergedVal # Update the primary tile
                nextTile  = 0 # Remove the secondary tile
                points   += temp_mergedVal # Update score
        # Remove middle 0s, add 0s back to fill
        self._compress_row(rowIndex)
        row += [0] * (self.cols - len(row))
        self.score += points # Update total score

    def _merge_board(self):
        ''' Wrapper that performs _merge_row on the whole board '''
        for row in range(self.rows):
            self._merge_row(row)

    def _transpose(self) -> None:
        ''' Returns the board with the row and column swapped '''
        self.board = [list(row) for row in zip(*self.board)] # Groups one index of each row in board

    def _reverse(self) -> None:
        ''' Reverses all the rows '''
        self.board = [row[::-1] for row in self.board]

    def _move_left(self):
        ''' Performs a left move '''
        self._merge_board() # Since the move method shifts to the left, there is no variation

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
        ''' Gets the tile value at a specific index '''
        return self.board[row][col]

    def _get_empty_cells(self) -> list[tuple[int, int]]:
        ''' Returns all the cells that has no numbers in it '''
        return [(r, c) for r in range(self.rows) for c in range(self.cols) if self.board[r][c] is None]

    def _set_tile(self, row: int, col: int, val: int) -> None:
        ''' Sets the values of a tile given the index '''
        self.board[row][col].value = val

    def _spawn_tile(self, num: int = 1) -> None:
        ''' Spawns new tiles IF the spot is empty '''
        empty = self._get_empty_cells()
        if not empty: 
            return
        
        for _ in range(num):
            randomTile = choice(empty)
            val = 4 if random() < 0.1 else 2
            self._set_tile(*randomTile, val)
            empty.remove(randomTile)


    ########## ========= WIN & LOSS ========= ##########

    def hasLegalMove(self) -> bool:
        ''' Checks if any moves are possible without altering the board '''
        for r in range(self.rows):
            for c in range(self.cols):
                # 1. If there's an empty space, a move is always possible
                if self.board[r][c] == 0:
                    return True
                
                # 2. Check horizontal neighbor (to the right)
                if c < self.cols - 1 and self.board[r][c] == self.board[r][c + 1]:
                    return True
                    
                # 3. Check vertical neighbor (below)
                if r < self.rows - 1 and self.board[r][c] == self.board[r + 1][c]:
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
        self.board     = [[Tile(0, (r, c), None, None, False) for c in range(self.cols)] for r in range(self.rows)]
        self.tileSpawn = tileSpawn
        self.score     = 0
        # Add starting tiles
        self._spawn_tile(2)


    ########## =========== DEBUG ============ ##########

    def _printBoard(self) -> None:
        ''' Debug function for printing '''
        buffer = []
        for row in self.board:
            buffer.append(f"{" ".join(map(str, row))}")
        rowLen = len(buffer[0])
        print('┌', '─' * (rowLen + 2), '┐', sep='')
        for row in buffer: print(f"│ {row} │")
        print('└', '─' * (rowLen + 2), '┘', sep='')