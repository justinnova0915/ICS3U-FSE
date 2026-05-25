'''
Class for the game board
'''

class Board:

    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.grid = [0 for i in range(row) for j in range(col)]
    
    
    def merge_row(self):
        newRow = [i for i in self.row if i != 0] # Remove initial zeros
        for i in range(len(newRow)-1): # For each pair check merge
            if newRow[i] == newRow[i+1]:
                newRow[i]  *= 2 # Merge by doubling value
                newRow[i+1] = 0
        print(newRow)
        newRow  = [i for i in newRow if i != 0] # Remove trailing zeros
        newRow += [0 for _ in range(len(self.row) - len(newRow))] # Add filler zeros
        self.row = newRow

