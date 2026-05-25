from constants import *

def compress_row(row: list[int]) -> list[int]:
    return [item for item in row if item != 0]

def merge_row(row: list[int]) -> tuple[list[int], int]:
    points = 0
    noZero = compress_row(row)
    # Merge for each valid pair
    for i in range(len(noZero) - 1):
        if noZero[i] == noZero[i+1]:
            mergedVal     = noZero[i] * 2
            noZero[i]     = mergedVal # Update the primary tile
            noZero[i+1]   = 0 # Remove the secondary tile
            points += mergedVal # Update score
    # Remove middle 0s, add 0s back to fill
    result  = compress_row(noZero)
    result += [0] * (len(row) - len(result))

    return result, points

def merge_board(board: list[list[int]]) -> tuple[list[list[int]], int]:
    points   = 0
    newBoard = []
    for row in board:
        merged, pts = merge_row(row)
        newBoard.append(merged)
        points += pts
    return newBoard, points

def _transpose(board: list[list[int]]) -> list[list[int]]:
    return [list(row) for row in zip(*board)] # Groups one index of each row in board

def move_left(board: list[list[int]]) -> tuple[list[list[int]], int]:
    return merge_board(board)

def move_right(board: list[list[int]]) -> tuple[list[list[int]], int]:
    board = [row[::-1] for row in board]
    newBoard, points = merge_board(board)
    return [row[::-1] for row in newBoard], points

def move_up(board: list[list[int]]) -> tuple[list[list[int]], int]:
    board = _transpose(board)
    newBoard, points = merge_board(board)
    return _transpose(newBoard), points

def move_down(board: list[list[int]]) -> tuple[list[list[int]], int]:
    board = [row[::-1] for row in _transpose(board)]
    newBoard, points = merge_board(board)
    return _transpose([row[::-1] for row in newBoard]), points

move_fn = {
    "left"  : move_left,
    "right" : move_right,
    "up"    : move_up,
    "down"  : move_down
}
def move(board: list[list[int]], direction: str) -> tuple[list[list[int]], int]:
    return move_fn[direction](board)

def hasLegalMove(board: list[list[int]]) -> bool: # Can another move happen?
    return any(
        move(board, direction)[0] != board # New position?
        for direction in MOVE_ACTIONS
    )