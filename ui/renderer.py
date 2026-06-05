import json

import pygame

from    constants       import *
from    game.board      import Board
from    game.state      import State
from    utils.tiles     import Tile
from    ui.uiObject     import *


class Renderer:
    ''' Class for rendering all surfaces onto the screen '''
    def __init__(self, screen: pygame.Surface, rows: int, cols: int) -> None:
        self.screen    = screen
        self.uiSurf    = pygame.Surface((600, 250), pygame.SRCALPHA)
        self.boardSurf = pygame.Surface(self._get_board_size(rows, cols), pygame.SRCALPHA)

        self.uiObjects : dict[str, uiObject | uiScore] = {
            "highscore" : uiScore((100, 40), "highscore"),
            "score"     : uiScore((100, 40), "score"),
        }
        self.uiObjects_pos : dict[str, tuple[int, int]] = {
            "highscore" : (475, 0),
            "score"     : (325, 0),
        }

        self.fontSurfaces = {
            key: pygame.font.Font(
                FONT_FILENAME,
                TILE_FONTSIZE[key]
            ).render(
                str(key),
                True,
                TILE_TEXT_COLOURS[
                    key if key in TILE_TEXT_COLOURS else "default"
                ]
            )
            for key in TILE_KEYS if key != "default"
        }
        self.fontDefault  = pygame.font.Font(FONT_FILENAME, TILE_FONTSIZE["default"])


    ########## ============ DRAW ============ ##########

    def draw(self, state: State, board: Board, tiles: list[Tile]) -> None:
        ''' Blits all surfaces onto the screen '''
        # Clear background
        self.screen.fill(BACKGROUND_COLOUR)
        self.boardSurf.fill((0, 0, 0, 0))
        self.uiSurf.fill((0, 0, 0, 0))
        # Render surfaces
        self._render_board(board, tiles)
        self._render_ui(board.score)
        # Blit surfaces
        self.screen.blit(self.boardSurf, self._get_board_pos())
        self.screen.blit(self.uiSurf, self._get_ui_pos())
    

    ########## =========== RENDER =========== ##########

    def _render_board(self, board: Board, tiles: list[Tile]):
        ''' Renders all board-related surfaces'''
        self._render_board_base(board)
        self._render_board_tiles(tiles)

    def _render_board_base(self, board: Board) -> None:
        ''' Renders the base board '''
        # Background
        pygame.draw.rect(self.boardSurf, BOARD_COLOUR, self.boardSurf.get_rect(), border_radius=BOARD_ROUND)
        # Null tiles
        for r, c in [(r, c) for r in range(board.rows) for c in range(board.cols)]:
            pygame.draw.rect(
                self.boardSurf,
                CELL_COLOUR,
                pygame.Rect(
                    c * (CELL_SIZE.w + CELL_PAD.w) + CELL_PAD.w,
                    r * (CELL_SIZE.h + CELL_PAD.h) + CELL_PAD.h,
                    *CELL_SIZE
                ),
                border_radius=CELL_ROUND
            )

    def _render_board_tiles(self, tiles: list[Tile]) -> None:
        ''' Renders the tiles on top of the board'''
        for tile in tiles:
            self._render_board_tile(tile)
    
    def _render_board_tile(self, tile: Tile) -> None:
        ''' Renders individual tiles on top of the board'''
        if tile.value != 0:
            rect = pygame.Rect(*tile.pos.to_int(), *tile.size)
            # Background
            colour = TILE_COLOURS.get(tile.value, TILE_COLOURS["default"])
            pygame.draw.rect(self.boardSurf, colour, rect, border_radius=CELL_ROUND)
            # Text
            textSurf = self._get_textSurface(tile.value)
            textRect = textSurf.get_rect()
            textRect.center = rect.center
            self.boardSurf.blit(textSurf, textRect)

    def _render_ui(self, score: int) -> None:
        ''' Renders all ui-related surfaces'''
        pygame.draw.rect(self.uiSurf, (255, 0, 0), (0, 0, *self.uiSurf.get_size()), 2)
        # Render individual surfaces
        self.uiObjects["score"].render(score)
        self.uiObjects["highscore"].render(HIGHSCORE)
        # Blit individual surfaces onto main surf
        for name in self.uiObjects.keys():
            self.uiSurf.blit(self.uiObjects[name].surf, self.uiObjects_pos[name])

    def _get_textSurface(self, value: int) -> pygame.Surface:
        ''' Renders the number surface of tiles'''
        if value not in self.fontSurfaces:
            self.fontSurfaces[value] = self.fontDefault.render(str(value), True, TILE_TEXT_COLOURS["default"])
        return self.fontSurfaces[value]
    
    
    ########## ====== POSITION & SIZE ======= ##########

    def resize(self, board: Board) -> None:
        self._resize_board(board.rows, board.cols)

    def _resize_board(self, rows: int, cols: int) -> None:
        self.boardsurf = pygame.Surface(self._get_board_size(rows, cols), pygame.SRCALPHA)

    def _get_board_size(self, rows: int, cols: int) -> Size:
        ''' Gets the size of the board surface '''
        return Size(
            cols * (CELL_SIZE.w + CELL_PAD.w) + CELL_PAD.w,
            rows * (CELL_SIZE.h + CELL_PAD.h) + CELL_PAD.h
        )
    
    def _get_board_pos(self) -> Coord:
        ''' Gets the position of the board surface'''
        uiHeight = self.uiSurf.get_height()
        return Coord(
            (self.screen.get_width()  - self.boardSurf.get_width())  // 2,
            uiHeight + (self.screen.get_height() - uiHeight - self.boardSurf.get_height()) // 2
        )

    def _get_ui_pos(self) -> Coord:
        ''' Gets the position of the ui surface '''
        return Coord(
            (self.screen.get_width() - self.uiSurf.get_width()) // 2, 0
        )
    