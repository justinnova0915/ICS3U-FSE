import pygame

from constants  import *
from ui.animator import Animator
from game.board import Board
from game.state import State
from utils.tiles import TileDraw

class Renderer:
    def __init__(self, screen: pygame.Surface, rows: int, cols: int) -> None:
        self.screen    = screen
        self.uiSurf    = pygame.Surface((800, 250), pygame.SRCALPHA)
        self.boardSurf = pygame.Surface(self._get_boardSize(rows, cols), pygame.SRCALPHA)

        self.fontSurfaces = {
            key: pygame.font.Font(
                FONT_FILENAME,
                TILE_FONT_SIZE[key]
            ).render(
                str(key),
                True,
                TILE_TEXT_COLOURS[
                    key if key in TILE_TEXT_COLOURS else "default"
                ]
            )
            for key in TILE_KEYS if key != "default"
        }
        self.fontDefault  = pygame.font.Font(FONT_FILENAME, TILE_FONT_SIZE["default"])

    def draw(self, board: Board, state: State) -> None:
        # Clear background
        self.screen.fill(BACKGROUND_COLOUR)
        self.boardSurf.fill((0, 0, 0, 0))
        self.uiSurf.fill((0, 0, 0, 0))
        # Render surfaces
        self._render_board(board)
        self._render_ui(board.score)
        # Blit surfaces
        self.screen.blit(self.boardSurf, self._get_boardPos())
        self.screen.blit(self.uiSurf, self._get_uiPos())

    def _get_textSurface(self, value: int) -> pygame.Surface:
        if value not in self.fontSurfaces:
            self.fontSurfaces[value] = self.fontDefault.render(str(value), True, TILE_TEXT_COLOURS["default"])
        return self.fontSurfaces[value]
 
    @staticmethod
    def _get_boardSize(rows: int, cols: int) -> Size:
        return Size(
            cols * (CELL_SIZE.w + CELL_PAD.w) + CELL_PAD.w,
            rows * (CELL_SIZE.h + CELL_PAD.h) + CELL_PAD.h
        )
    
    def _get_boardPos(self) -> Coord:
        uiHeight = self.uiSurf.get_height()
        return Coord(
            (self.screen.get_width()  - self.boardSurf.get_width())  // 2,
            uiHeight + (self.screen.get_height() - uiHeight - self.boardSurf.get_height()) // 2
        )

    def _get_uiPos(self) -> Coord:
        return Coord(
            (self.screen.get_width() - self.uiSurf.get_width()) // 2,
            0
        )

    def gridToPixel(self, board: Board, row : int, col : int) -> Coord:
        boardPos = self._get_boardPos(board.rows, board.cols)
        x = boardPos.x + (CELL_PAD.w + (CELL_SIZE.w + CELL_PAD.w) * col)
        y = boardPos.y + (CELL_PAD.h + (CELL_SIZE.h + CELL_PAD.h) * row)
        return Coord(x, y)
    
    def _render_base(self, board: Board) -> None:
        pygame.draw.rect(self.boardSurf, BOARD_COLOUR, self.boardSurf.get_rect(), border_radius=BOARD_ROUND)
        # Individual tiles
        for r, c in [(r, c) for r in range(board.rows) for c in range(board.cols)]:
            rect = pygame.Rect(c * (CELL_SIZE.w + CELL_PAD.w) + CELL_PAD.w, r * (CELL_SIZE.h + CELL_PAD.h) + CELL_PAD.h, *CELL_SIZE)
            # Null background
            pygame.draw.rect(self.boardSurf, BOARD_TILE_COLOUR, rect, border_radius=BOARD_TILE_ROUND)
    
    def _render_tile(self, tile: TileDraw):
        if tile.value != 0:
            rect = pygame.Rect(tile.x, tile.y, *CELL_SIZE)
            # Background
            colour = TILE_COLOURS.get(tile.value, TILE_COLOURS["default"])
            pygame.draw.rect(self.boardSurf, colour, rect, border_radius=BOARD_TILE_ROUND)
            # Text
            textSurf = self._get_textSurface(tile.value)
            textRect = textSurf.get_rect()
            textRect.center = rect.center
            self.boardSurf.blit(textSurf, textRect)

    def _render_tiles(self, tiles: list[TileDraw]):
        for tile in tiles:
            self._render_tile(tile)                

    def _render_ui(self, score: int) -> None:
        # Scores
        textSurf = self.fontDefault.render(str(score), True, TILE_FONT_SIZE["default"])
        self.uiSurf.blit(textSurf, (100, 0))