from   pathlib     import Path

from   utils.namedpair  import Size, Coord

ROOT_PATH = str(Path(__file__).parent)

def pathJoin(root: str | Path, path: str, *args) -> str:
    res = Path(root) / path
    for p in args:
        res = res / p
    return str(res)

SCREEN_SIZE  = Size(900, 1000)

########## ============= UI ============= ##########

FONT_FILENAME = pathJoin(ROOT_PATH, "assets", "clearSans.ttf")
FONTSIZE      = 36

BACKGROUND_COLOUR = (250, 248, 239)

SCORE_BGCOLOUR     = (250, 248, 239)
SCORE_OUTCOLOUR    = (234, 230, 218)
SCORE_COLOUR_TITLE = (156, 137, 121)
SCORE_COLOUR_SCORE = (156, 137, 121)


########## ======== BOARD & CELL ======== ##########

BOARD_ROUND  = 25
BOARD_PAD    = Size(20,  20 )
BOARD_COLOUR = (156, 137, 121)

CELL_SIZE   = Size(125, 125)
CELL_PAD    = Size(15,  15 )
CELL_ROUND  = 10
CELL_COLOUR = (189, 172, 151)


########## =========== TILES ============ ##########

TILE_KEYS = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, "default"]

TILE_FONTSIZE_LARGE  = 50   # 2, 4 ... 64
TILE_FONTSIZE_MEDIUM = 46   # 128, 256, 512
TILE_FONTSIZE_SMALL  = 36   # 1024, 2048+

TILE_FONTSIZE = {
    2:         TILE_FONTSIZE_LARGE,
    4:         TILE_FONTSIZE_LARGE,
    8:         TILE_FONTSIZE_LARGE,
    16:        TILE_FONTSIZE_LARGE,
    32:        TILE_FONTSIZE_LARGE,
    64:        TILE_FONTSIZE_LARGE,
    128:       TILE_FONTSIZE_MEDIUM,
    256:       TILE_FONTSIZE_MEDIUM,
    512:       TILE_FONTSIZE_MEDIUM,
    1024:      TILE_FONTSIZE_SMALL,
    2048:      TILE_FONTSIZE_SMALL,
    "default": TILE_FONTSIZE_SMALL,
}

TILE_COLOURS = {
    2:         (238, 228, 218),
    4:         (237, 224, 200),
    8:         (242, 177, 121),
    16:        (245, 149, 99 ),
    32:        (246, 124, 95 ),
    64:        (246, 90,  60 ),
    128:       (237, 207, 114),
    256:       (237, 204, 97 ),
    512:       (237, 200, 80 ),
    1024:      (237, 197, 63 ),
    2048:      (237, 194, 46 ),
    "default": (60, 58, 50),  # for tiles beyond 2048
}

TILE_TEXT_COLOURS = {
    2:         (119, 110, 101),
    4:         (119, 110, 101),
    "default": (249, 246, 242),
}

########## ========= CONSTANTS ========== ##########

ANIMATION_DURATION = 0.20

WIN_TILE = 2048

MOVE_ACTIONS = ["left", "right", "up", "down"]