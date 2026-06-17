from    typing  import overload, Callable, Any, Literal

import  pygame

from    constants       import *
from    utils.namedpair import Size, Coord
from    utils.tiles     import Tile
from    utils.lerp      import animate
from    ui.uiObject     import UIObject, UIScore, UIText
from    game.state      import State
from    game.board      import Board


class RendererManager:
    ''' Maintains a copy of all state-specific Renderer objects '''
    
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen

        self.menu = MenuRenderer(screen)
        self.game = GameRenderer(screen)
        self.win  = WinRenderer(screen)
        self.lose = LoseRenderer(screen)
    

    @overload
    def render(self, state: Literal[State.MENU]) -> None: ...
    @overload
    def render(self, state: Literal[State.GAME], board: Board, tiles: list[Tile], score: int, highscore: int) -> None: ...
    @overload
    def render(self, state: Literal[State.WIN]) -> None: ...
    @overload
    def render(self, state: Literal[State.LOSE], score: int, moves: int, onClick: Callable) -> None: ...

    def render(self, state: State, *args: Any) -> None:
        ''' Blits all rendered surfaces onto the screen '''
        # Clear background
        self.screen.fill(BG_COLOUR)
        # Render surfaces
        match state:
            case State.MENU:
                self.menu.render(*args)
                ...
            case State.GAME:
                self.game.render(*args)
                ...
            case State.WIN:
                self.win.render(*args)
                ...
            case State.LOSE:
                self.lose.render(*args)
                ...


class Renderer:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen

    def render(self) -> None:
        ''' Renders all surfaces onto the screen '''
        # Clear background
        self.screen.fill(BG_COLOUR)
        ...


class MenuRenderer(Renderer):
    ''' Renderer object for all 'MENU' state surfaces '''

    def __init__(self, screen: pygame.Surface) -> None:
        super().__init__(screen)
        self.surface = pygame.Surface(self.screen.size, pygame.SRCALPHA)

        self.uiObjects : dict[str, UIText]= {
            
        }

    def render(self) -> None:
        super().render()
        ...

class GameRenderer(Renderer):
    ''' Renderer object for all 'GAME' state surfaces '''

    def __init__(self, screen: pygame.Surface, Board: Board) -> None:
        super().__init__(screen)

        # Surfaces
        self.uiSurf    = pygame.Surface((575, 250), pygame.SRCALPHA)
        self.boardSurf = pygame.Surface(self._get_boardSize(Board.rows, Board.cols), pygame.SRCALPHA)

        # Ui objects
        self.uiObjects : dict[str, UIScore] = {
            "score"     : UIScore((125, 60), (150, 50), "SCORE"),
            "highscore" : UIScore((125, 60), (300, 50), "BEST", border=True),
        }

        # Tile text cache
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


    ########## =========== RENDER =========== ##########

    def render(self, board: Board, tiles: list[Tile], score: int, highscore: int) -> None:
        super().render()

        self._renderBoard(board, tiles)
        self._renderUi(score, highscore)

    def _renderBoard(self, board: Board, tiles: list[Tile]) -> None:
        ''' Renders the board for 'GAME' state '''

        self._renderBoard_base(board)
        self._renderBoard_tiles(tiles)

    def _renderUi(self, score: int, highscore: int) -> None:
        ''' Renders the ui for 'GAME' state '''
        
        # Render individual surfaces
        self.uiObjects["score"].render(score)
        self.uiObjects["highscore"].render(highscore)
        # Blit individual surfaces onto main surf
        for name in self.uiObjects.keys():
            self.uiSurf.blit(self.uiObjects[name].surface, self.uiObjects[name].pos)

    
    def _renderBoard_base(self, board: Board) -> None:
        ''' Renders the base board '''

        # Background
        pygame.draw.rect(self.boardSurf, BOARD_COLOUR, self.boardSurf.get_rect(), border_radius=BOARD_ROUND)

        # Cells
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

    def _renderBoard_tiles(self, tiles: list[Tile]) -> None:
        ''' Renders the tiles on top of the board'''

        for tile in tiles:
            # Don't render null tiles
            if tile.value != 0:
                self.boardSurf.blit(
                    self._get_tileSurface(tile.value),
                    pygame.Rect(*tile.pos.to_int(), *tile.size)
                )

    def _get_tileSurface(self, value: int) -> pygame.Surface:
        ''' Renders the number surface of tiles'''

        surface = pygame.Surface(CELL_SIZE, pygame.SRCALPHA)

        # Background
        pygame.draw.rect(
            surface,
            TILE_COLOURS.get(value, TILE_COLOURS["default"]),
            surface.get_rect(),
            border_radius=CELL_ROUND
        )
        
        # Number
        if value not in self.fontSurfaces:
            self.fontSurfaces[value] = self.fontDefault.render(str(value), True, TILE_TEXT_COLOURS["default"])
        textSurf = self.fontSurfaces[value]
        textRect = textSurf.get_rect()
        textRect.center = surface.get_rect().center
        self.boardSurf.blit(textSurf, textRect)

        return surface

    ########## ====== POSITION & SIZE ======= ##########

    def _get_boardSize(self, rows: int, cols: int) -> Size:
        ''' Gets the size of the board surface '''

        return Size(
            cols * (CELL_SIZE.w + CELL_PAD.w) + CELL_PAD.w,
            rows * (CELL_SIZE.h + CELL_PAD.h) + CELL_PAD.h
        )
    
    def _get_boardPos(self) -> Coord:
        ''' Gets the position of the board surface'''

        uiHeight = self.uiSurf.get_height()
        return Coord(
            (self.screen.get_width()  - self.boardSurf.get_width())  // 2,
            uiHeight + (self.screen.get_height() - uiHeight - self.boardSurf.get_height()) // 2
        )

    def _get_uiPos(self) -> Coord:
        ''' Gets the position of the ui surface '''

        return Coord(
            (self.screen.get_width() - self.uiSurf.get_width()) // 2, 0
        )


class WinRenderer(Renderer):
    ''' Renderer object for all 'WIN' state surfaces '''

    def __init__(self, screen: pygame.Surface) -> None:

        super().__init__(screen)
        
        # Surfaces
        self.surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)

        # Animation
        self.win_anim_t = 0.0

        self.restartButton_x = 250
        self.restartButton_y = 50

        self.gameOver_y = -50
        self.gameOver_Target_y = 50

        self.score_start_y = -50
        self.score_target_y = 150

        self.restart_start_y = -50
        self.restart_target_y = 280

        # Font cache
        self.gameOverFont = pygame.font.Font(FONT_FILENAME, 100)
        self.scoreFont = pygame.font.Font(FONT_FILENAME, 20)
        self.restartTextFont = pygame.font.Font(FONT_FILENAME, 25)

    def render(self, score: int, moves: int, onClick) -> None:

        super().render()
        
        if self.win_anim_t < 1.0:
            self.win_anim_t += 0.04
            if self.win_anim_t > 1.0:
                self.win_anim_t = 1.0

        gameOverText = self.gameOverFont.render("You win!", True, (156, 137, 121))
        scoreText = self.scoreFont.render(f"You scored {score} points in {moves} moves.", True, (156, 137, 121))
        restartText = self.restartTextFont.render("Play Again", True, (156, 137, 121))

        self.restartSurf = pygame.Surface((self.restartButton_x, self.restartButton_y), pygame.SRCALPHA)
        pygame.draw.rect(self.restartSurf, BG_COLOUR, (0, 0, self.restartButton_x, self.restartButton_y), border_radius=15)
        pygame.draw.rect(self.restartSurf, SCORE_BGCOLOUR, (0, 0, self.restartButton_x, self.restartButton_y), border_radius=15, width=5)
        self.restartSurf.blit(restartText, (65, 5))

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        is_hovered = pygame.Rect(SCREEN_SIZE.w/2 - self.restartButton_x/2, self.restart_target_y - self.restartButton_y/2, self.restartButton_x, self.restartButton_y).collidepoint(mouse_pos)

        if is_hovered and mouse_clicked:
            onClick()

        self.screen.blit(*animate(self.win_anim_t, gameOverText, (SCREEN_SIZE.w / 2, self.gameOver_y), (SCREEN_SIZE.w / 2, self.gameOver_Target_y)))
        self.screen.blit(*animate(self.win_anim_t, scoreText, (SCREEN_SIZE.w / 2, self.score_start_y), (SCREEN_SIZE.w / 2, self.score_target_y)))
        self.screen.blit(*animate(self.win_anim_t, self.restartSurf, (SCREEN_SIZE.w / 2, self.restart_start_y), (SCREEN_SIZE.w / 2, self.restart_target_y)))


class LoseRenderer(Renderer):
    ''' Renderer object for all 'LOSE' state surfaces '''

    def __init__(self, screen: pygame.Surface) -> None:

        super().__init__(screen)
        
        # Surfaces
        self.surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)

        # Animation
        self.win_anim_t = 0.0

        self.restartButton_x = 250
        self.restartButton_y = 50

        self.gameOver_y = -50
        self.gameOver_Target_y = 50

        self.score_start_y = -50
        self.score_target_y = 150

        self.restart_start_y = -50
        self.restart_target_y = 280

        # Font cache
        self.gameOverFont = pygame.font.Font(FONT_FILENAME, 100)
        self.scoreFont = pygame.font.Font(FONT_FILENAME, 20)
        self.restartTextFont = pygame.font.Font(FONT_FILENAME, 25)

    def render(self, score: int, moves: int, onClick) -> None:

        super().render()
        
        if self.win_anim_t < 1.0:
            self.win_anim_t += 0.04
            if self.win_anim_t > 1.0:
                self.win_anim_t = 1.0

        gameOverText = self.gameOverFont.render("Game Over", True, (156, 137, 121))
        scoreText = self.scoreFont.render(f"You scored {score} points in {moves} moves.", True, (156, 137, 121))
        restartText = self.restartTextFont.render("Play Again", True, (156, 137, 121))

        self.restartSurf = pygame.Surface((self.restartButton_x, self.restartButton_y), pygame.SRCALPHA)
        pygame.draw.rect(self.restartSurf, BG_COLOUR, (0, 0, self.restartButton_x, self.restartButton_y), border_radius=15)
        pygame.draw.rect(self.restartSurf, SCORE_BGCOLOUR, (0, 0, self.restartButton_x, self.restartButton_y), border_radius=15, width=5)
        self.restartSurf.blit(restartText, (65, 5))

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        is_hovered = pygame.Rect(SCREEN_SIZE.w/2 - self.restartButton_x/2, self.restart_target_y - self.restartButton_y/2, self.restartButton_x, self.restartButton_y).collidepoint(mouse_pos)

        if is_hovered and mouse_clicked:
            onClick()

        self.screen.blit(*animate(self.win_anim_t, gameOverText, (SCREEN_SIZE.w / 2, self.gameOver_y), (SCREEN_SIZE.w / 2, self.gameOver_Target_y)))
        self.screen.blit(*animate(self.win_anim_t, scoreText, (SCREEN_SIZE.w / 2, self.score_start_y), (SCREEN_SIZE.w / 2, self.score_target_y)))
        self.screen.blit(*animate(self.win_anim_t, self.restartSurf, (SCREEN_SIZE.w / 2, self.restart_start_y), (SCREEN_SIZE.w / 2, self.restart_target_y)))
