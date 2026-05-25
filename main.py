import pygame

def merge_row(row: list[int]) -> list[int]:
    newRow = [i for i in row if i != 0] # Remove initial zeros
    for i in range(len(newRow)-1): # For each pair check merge
        if newRow[i] == newRow[i+1]:
            newRow[i]  *= 2 # Merge by doubling value
            newRow[i+1] = 0
    print(newRow)
    newRow  = [i for i in row if i != 0] # Remove trailing zeros
    newRow += [0 for _ in range(len(row) - len(newRow))] # Add filler zeros
    return newRow

