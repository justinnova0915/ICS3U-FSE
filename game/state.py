from enum import Enum, auto

class State(Enum):
    MENU = auto()
    GAME = auto()
    WIN  = auto()
    LOSE = auto()