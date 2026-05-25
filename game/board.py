from random import choice, random

from constants import *
from . import logic

class Board:
    def __init__(self, rows: int = 4, cols: int = 4, tileSpawn: int = 1) -> None:
        self.rows      : int
        self.cols      : int
        self.board     : list[list[int]]
        self.tileSpawn : int
        self.score     : int
        self.win       : bool
        self.lose      : bool
        self.reset(rows, cols, tileSpawn)

    def reset(self, rows: int = 4, cols: int = 4, tileSpawn: int = 1) -> None:
        self.rows      = rows
        self.cols      = cols
        self.board     = [[0 for _ in range(cols)] for _ in range(rows)]
        self.tileSpawn = tileSpawn
        self.score     = 0
        self.win       = False
        self.lose      = False
        # Add starting tiles
        self.add_tile(2)

    def get_tile(self, row: int, col: int) -> int:
        return self.board[row][col]

    def get_empty(self) -> list[tuple[int, int]]:
        return [(r, c) for r in range(self.rows) for c in range(self.cols) if self.board[r][c] == 0]
    
    def set_tile(self, row: int, col: int, val: int) -> None:
        self.board[row][col] = val

    def add_tile(self, num: int = 1) -> None:
        empty = self.get_empty()
        for _ in range(num):
            if not empty: return # Empty
            pos = choice(empty)
            val = 4 if random() < 0.1 else 2
            self.set_tile(*pos, val)
            empty.remove(pos)

    def move(self, direction: str) -> bool: # Did a move happen?
        newBoard, points = logic.move(self.board, direction)
        # Don't update if no move
        if self.board == newBoard:
            return False
        # Update board, update score, add tile
        self.board = newBoard
        self.score += points
        self.add_tile(self.tileSpawn)
        # Check if win or lose
        if self._hasWon(): # Win tile achieved
            self.win = True
        if not logic.hasLegalMove(self.board): # No legal moves
            self.lose = True
        return True

    def _hasWon(self) -> bool:
        return any(
            self.get_tile(r, c) == WIN_TILE
            for r in range(self.rows)
            for c in range(self.cols)
        )
    
    @staticmethod
    def _printBoard(board: list[list[int]]) -> None:
        buffer = []
        for row in board:
            buffer.append(f"{" ".join(map(str, row))}")
        rowLen = len(buffer[0])
        print('┌', '─' * (rowLen + 2), '┐', sep='')
        for row in buffer: print(f"│ {row} │")
        print('└', '─' * (rowLen + 2), '┘', sep='')