from random import choice, random
from constants import *

class Board:
    '''
    Main class for the game board
    '''
    def __init__(self, rows: int = 4, cols: int = 4, tileSpawn: int = 1) -> None:
        self.rows      : int
        self.cols      : int
        self.board     : list[list[int]]
        self.move_func = {
            '''dict of all the directions with their respective functions'''
            "left"  : self._move_left,
            "right" : self._move_right,
            "up"    : self._move_up,
            "down"  : self._move_down
        }
        self.tileSpawn : int
        self.score     : int
        self.win       : bool
        self.lose      : bool
        self.reset(rows, cols, tileSpawn)

    ########## ========= PRIVATE FUNCTIONS ========= ##########

    @staticmethod
    def _printBoard(self, board: list[list[int]]) -> None:
        '''Debug function for printing'''
        buffer = []
        for row in board:
            buffer.append(f"{" ".join(map(str, row))}")
        rowLen = len(buffer[0])
        print('┌', '─' * (rowLen + 2), '┐', sep='')
        for row in buffer: print(f"│ {row} │")
        print('└', '─' * (rowLen + 2), '┘', sep='')

    def _compress_row(self, row: int) -> list[int]:
        '''removes the zeros from a row'''
        return [item for item in row if item != 0]

    def _merge_row(self, row: list[int]) -> tuple[list[int], int]:
        '''Base logic for merging'''
        points = 0
        noZero = self._compress_row(row)
        # Merge for each valid pair
        for i in range(len(noZero) - 1):
            if noZero[i] == noZero[i+1]:
                mergedVal     = noZero[i] * 2
                noZero[i]     = mergedVal # Update the primary tile
                noZero[i+1]   = 0 # Remove the secondary tile
                points += mergedVal # Update score
        # Remove middle 0s, add 0s back to fill
        result  = self._compress_row(noZero)
        result += [0] * (len(row) - len(result))

        return result, points

    def _merge_board(self, board: list[list[int]]) -> tuple[list[list[int]], int]:
        '''Wrapper that performs _merge_row on the whole board'''
        points   = 0
        newBoard = []
        for row in board:
            merged, pts = self._merge_row(row)
            newBoard.append(merged)
            points += pts
        return newBoard, points

    def _transpose(self, board: list[list[int]]) -> list[list[int]]:
        '''Returns the board with the row and column swapped'''
        return [list(row) for row in zip(*board)] # Groups one index of each row in board

    def _move_left(self, board: list[list[int]]) -> tuple[list[list[int]], int]:
        '''
        Performs a left move

        Since the move method starts to the left, there is no left variation
        '''
        return self._merge_board(board)

    def _move_right(self, board: list[list[int]]) -> tuple[list[list[int]], int]:
        '''Performs a right move'''
        board = [row[::-1] for row in board]
        newBoard, points = self._merge_board(board)
        return [row[::-1] for row in newBoard], points

    def _move_up(self, board: list[list[int]]) -> tuple[list[list[int]], int]:
        '''Performs a up move'''
        board = self._transpose(board)
        newBoard, points = self._merge_board(board)
        return self._transpose(newBoard), points

    def _move_down(self, board: list[list[int]]) -> tuple[list[list[int]], int]:
        '''Performs a down move'''
        board = [row[::-1] for row in self._transpose(board)]
        newBoard, points = self._merge_board(board)
        return self._transpose([row[::-1] for row in newBoard]), points

    def reset(self, rows: int = 4, cols: int = 4, tileSpawn: int = 1) -> None:
        '''
        Reverts the game state to inital state and clears the board
        '''
        self.rows      = rows
        self.cols      = cols
        self.board     = [[0 for _ in range(cols)] for _ in range(rows)]
        self.tileSpawn = tileSpawn
        self.score     = 0
        self.win       = False
        self.lose      = False
        # Add starting tiles
        self.spawn_tile(2)

    def get_tile(self, row: int, col: int) -> int:
        '''Gets the tile value at a specific index'''
        return self.board[row][col]

    def get_empty_board(self) -> list[tuple[int, int]]:
        '''HELPER: returns a grid of all zeros'''
        return [(r, c) for r in range(self.rows) for c in range(self.cols) if self.board[r][c] == 0]
    
    def set_tile(self, row: int, col: int, val: int) -> None:
        '''Sets the values of a tile given the index'''
        self.board[row][col] = val

    def spawn_tile(self, num: int = 1) -> None:
        '''Spawns a new tile at the given index IF the spot is empty'''
        empty = self.get_empty_board()
        for _ in range(num):
            if not empty: return # Empty
            pos = choice(empty)
            val = 4 if random() < 0.1 else 2
            self.set_tile(*pos, val)
            empty.remove(pos)

    def move(self, direction: str) -> bool: # Did a move happen?
        '''Exposed enpoint for moving provided a direction'''
        newBoard, points = self.move_func[direction](self.board)
        # Don't update if no move
        if self.board == newBoard:
            return False
        
        # Update board, update score, add tile
        self.board = newBoard
        self.score += points
        self.spawn_tile(self.tileSpawn)

        # Check if win or lose
        if self.hasWon(): # Win tile achieved
            self.win = True
        if not self.hasLegalMove(self.board): # No legal moves
            self.lose = True
        return True

    def hasLegalMove(self, board: list[list[int]]) -> bool: # Can another move happen?
        return any(
            self.move(board, direction)[0] != board # New position?
            for direction in MOVE_ACTIONS
        )

    def hasWon(self) -> bool:
        '''Check if the user has won'''
        return any(
            self.get_tile(r, c) == WIN_TILE
            for r in range(self.rows)
            for c in range(self.cols)
        )