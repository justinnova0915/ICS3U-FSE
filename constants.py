from pathlib     import Path
from collections import namedtuple

ROOT_PATH = str(Path(__file__).parent)

def pathJoin(root: str | Path, path: str, *args) -> str:
    res = Path(root) / path
    for p in args:
        res = res / p
    return str(res)

Coord    = namedtuple("Coord",      ['x', 'y'])
Size     = namedtuple("Size",       ['w', 'h'])

def easeOut_back(t: float) -> float:
    c1 = 0.5
    c3 = c1 + 1.0
    return 1.0 + c3 * ((t - 1.0) ** 3) + c1 * ((t - 1.0) ** 2)

FONT_FILENAME = pathJoin(ROOT_PATH, "assets", "clearSans.ttf")

WIN_TILE = 2048

MOVE_ACTIONS = ["left", "right", "up", "down"]

BACKGROUND_COLOUR = (250, 248, 239)

BOARD_COLOUR = (156, 137, 121)
BOARD_TILE_COLOUR = (189, 172, 151)
BOARD_ROUND = 25
BOARD_TILE_ROUND = 10

TILE_KEYS = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, "default"]

TILE_FONT_LARGE  = 50   # 2, 4 ... 64
TILE_FONT_MEDIUM = 46   # 128, 256, 512
TILE_FONT_SMALL  = 36   # 1024, 2048+

TILE_FONT = {
    2:    TILE_FONT_LARGE,
    4:    TILE_FONT_LARGE,
    8:    TILE_FONT_LARGE,
    16:   TILE_FONT_LARGE,
    32:   TILE_FONT_LARGE,
    64:   TILE_FONT_LARGE,
    128:  TILE_FONT_MEDIUM,
    256:  TILE_FONT_MEDIUM,
    512:  TILE_FONT_MEDIUM,
    1024: TILE_FONT_SMALL,
    2048: TILE_FONT_SMALL,
    "default": TILE_FONT_SMALL,
}

TILE_COLOURS = {
    2:    (238, 228, 218),
    4:    (237, 224, 200),
    8:    (242, 177, 121),
    16:   (245, 149, 99 ),
    32:   (246, 124, 95 ),
    64:   (246, 90,  60 ),
    128:  (237, 207, 114),
    256:  (237, 204, 97 ),
    512:  (237, 200, 80 ),
    1024: (237, 197, 63 ),
    2048: (237, 194, 46 ),
    "default": (60, 58, 50),  # for tiles beyond 2048
}

TILE_TEXT_COLOURS = {
    2:         (119, 110, 101),
    4:         (119, 110, 101),
    "default": (249, 246, 242),
}

CELL_SIZE = Size (125, 125)
CELL_PAD  = Size (15,  15 )