import  pygame

from    constants       import *
from    utils.namedpair import Size, Coord
from    utils.vector    import Vector
from    utils.lerp      import animate
from    ui.uiObject     import UIObject, UIScore, UIRect
from    game.state      import State
from    game.board      import Board
from    utils.tiles     import Tile


class Renderer:
    ''' Class for rendering all surfaces onto the screen '''
    def __init__(self, screen: pygame.Surface, rows: int, cols: int, state) -> None:
        self.screen    = screen
        self.uiSurf    = pygame.Surface((575, 250), pygame.SRCALPHA)
        self.boardSurf = pygame.Surface(self._get_board_size(rows, cols), pygame.SRCALPHA)
        self.menuSurf  = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        self.restartSurf: pygame.Surface

        self.state     = state

        self.uiObjects : dict[str, UIScore] = {
            "score"     : UIScore(Size(125, 60), Vector(150, 155), "SCORE", SCORE_TITLECOLOUR, SCORE_SCORECOLOUR, SCORE_BGCOLOUR),
            "highscore" : UIScore(Size(125, 60), Vector(300, 155), "BEST",  SCORE_TITLECOLOUR, SCORE_SCORECOLOUR, SCORE_BGCOLOUR, 2, SCORE_OUTCOLOUR),
        }

        self.win_anim_t = 0.0

        self.gameOverFont = pygame.font.Font(FONT_FILENAME, 100)
        self.scoreFont = pygame.font.Font(FONT_FILENAME, 20)
        self.restartTextFont = pygame.font.Font(FONT_FILENAME, 25)

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

    def reset(self, screen: pygame.Surface, rows: int, cols: int, state):
        self.uiSurf    = pygame.Surface((575, 250), pygame.SRCALPHA)
        self.boardSurf = pygame.Surface(self._get_board_size(rows, cols), pygame.SRCALPHA)
        self.menuSurf  = pygame.Surface(screen.size, pygame.SRCALPHA)
        self.restartSurf: pygame.Surface
        self.state = state
        self.win_anim_t = 0.0

    ########## ============ DRAW ============ ##########

    def render(self, state: State, board: Board, tiles: list[Tile], highscore: int, on_click) -> None:
        ''' Blits all surfaces onto the screen '''
        # Clear background
        self.screen.fill(BACKGROUND_COLOUR)
        self.boardSurf.fill((0, 0, 0, 0))
        self.uiSurf   .fill((0, 0, 0, 0))
        # DEBUG
        pygame.draw.rect(self.boardSurf, (255, 0, 0), self.boardSurf.get_rect(), 2)
        pygame.draw.rect(self.uiSurf, (0, 0, 255), self.uiSurf.get_rect(), 2)
        # Render surfaces
        match state:
            case State.MENU:
                ...
            case State.GAME:
                self._renderUi_GAME(board.score, highscore)
                self._renderBoard_GAME(board, tiles)
            case State.WIN:
                ...
            case State.LOSE:
                self._renderUi_LOSE(board.score, board.moves, on_click)
                self._renderBoard_LOSE(board, tiles)
        # Blit surfaces
        self.screen.blit(self.boardSurf, self._get_board_pos())
        self.screen.blit(self.uiSurf, self._get_ui_pos())            
    

    ########## =========== RENDER =========== ##########

    def _renderBoard_GAME(self, board: Board, tiles: list[Tile]):
        ''' Renders the board for 'GAME' state '''
        self._renderBoard_base(board)
        self._renderBoard_tiles(tiles)

    def _renderBoard_LOSE(self, board: Board, tiles: list[Tile]):
        ''' Renders the board for 'LOSE' state '''
        self._renderBoard_base(board)
        self._renderBoard_tiles(tiles)

    def _renderBoard_base(self, board: Board) -> None:
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

    def _renderBoard_tiles(self, tiles: list[Tile]) -> None:
        ''' Renders the tiles on top of the board'''
        for tile in tiles:
            self._renderBoard_tile(tile)
    
    def _renderBoard_tile(self, tile: Tile) -> None:
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

    def _renderUi_MENU(self) -> None: ...

    def _renderUi_GAME(self, currScore: int, highscore: int) -> None:
        ''' Renders the ui for 'GAME' state '''
        # Render individual surfaces
        self.uiObjects["score"].render(score=currScore)
        self.uiObjects["highscore"].render(score=highscore)
        # Blit individual surfaces onto main surf
        for name in self.uiObjects.keys():
            self.uiSurf.blit(self.uiObjects[name].surface, self.uiObjects[name].pos.to_int())

    def _renderUi_WIN(self) -> None: ...
    
    def _renderUi_LOSE(self, score: int, moves: int, on_click) -> None:
        ''' Renders the ui for 'LOSE' state '''
        if self.win_anim_t < 1.0:
            self.win_anim_t += 0.04
            if self.win_anim_t > 1.0:
                self.win_anim_t = 1.0

        gameOverText = self.gameOverFont.render("Game Over", True, (156, 137, 121))
        scoreText = self.scoreFont.render(f"You scored {score} points in {moves} moves.", True, (156, 137, 121))
        restartText = self.restartTextFont.render("Play Again", True, (156, 137, 121))

        restartButton_x = 250
        restartButton_y = 50

        gameOver_y = -50
        gameOver_Target_y = 50
        
        score_start_y = -50
        score_target_y = 150

        restart_start_y = -50
        restart_target_y = 280

        self.restartSurf = pygame.Surface((restartButton_x, restartButton_y), pygame.SRCALPHA)
        pygame.draw.rect(self.restartSurf, BACKGROUND_COLOUR, (0, 0, restartButton_x, restartButton_y), border_radius=15)
        pygame.draw.rect(self.restartSurf, SCORE_BGCOLOUR, (0, 0, restartButton_x, restartButton_y), border_radius=15, width=5)
        self.restartSurf.blit(restartText, (65, 5))

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        is_hovered = pygame.Rect(SCREEN_SIZE.w/2 - restartButton_x/2, restart_target_y - restartButton_y/2, restartButton_x, restartButton_y).collidepoint(mouse_pos)

        if is_hovered and mouse_clicked:
            on_click()
        

        self.screen.blit(*animate(self.win_anim_t, gameOverText, (SCREEN_SIZE.w / 2, gameOver_y), (SCREEN_SIZE.w / 2, gameOver_Target_y)))
        self.screen.blit(*animate(self.win_anim_t, scoreText, (SCREEN_SIZE.w / 2, score_start_y), (SCREEN_SIZE.w / 2, score_target_y)))
        self.screen.blit(*animate(self.win_anim_t, self.restartSurf, (SCREEN_SIZE.w / 2, restart_start_y), (SCREEN_SIZE.w / 2, restart_target_y)))


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
