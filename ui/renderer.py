import json

import pygame

from    constants       import *
from    game.board      import Board
from    game.state      import State
from    utils.tiles     import Tile
from    ui.uiObject     import uiObject, uiScore
from    utils.lerp      import animate


class Renderer:
    ''' Class for rendering all surfaces onto the screen '''
    def __init__(self, screen: pygame.Surface, rows: int, cols: int, state, mouse_pos) -> None:
        self.screen    = screen
        self.uiSurf    = pygame.Surface((575, 250), pygame.SRCALPHA)
        self.boardSurf = pygame.Surface(self._get_board_size(rows, cols), pygame.SRCALPHA)
        self.menuSurf  = pygame.Surface(screen.size, pygame.SRCALPHA)
        self.startSurf: pygame.Surface
        self.restartSurf: pygame.Surface
        self.state = state
        self.mouse_pos = mouse_pos

        # for _render_dialog() 
        self.active = False
        self.fieldString = ""
        self.saved = False

        with open("./best.txt") as scoreFile:
            self.leaderboard = [tuple(line.strip("\n").split(",")) for line in scoreFile.readlines()]

        self.uiObjects : dict[str, uiObject | uiScore] = {
            "score"     : uiScore((125, 60), (150, 50), "SCORE"),
            "highscore" : uiScore((125, 60), (300, 50), "BEST", width=2),
        }

        self.win_anim_t = 0.0

        self.gameOverFont = pygame.font.Font(FONT_FILENAME, 100)
        self.scoreFont = pygame.font.Font(FONT_FILENAME, 20)
        self.restartTextFont = pygame.font.Font(FONT_FILENAME, 25)
        self.leaderboardFont = pygame.font.Font(FONT_FILENAME, 25)
        self.titleFont = pygame.font.Font(FONT_FILENAME, 30)



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
        self.startSurf: pygame.Surface
        self.state = state
        self.win_anim_t = 0.0
        self.saved = False

    ########## ============ DRAW ============ ##########

    def draw(self, state: State, board: Board, tiles: list[Tile], restart_on_click, menu_on_click, events: list[pygame.Event], mouse_pos) -> None:
        ''' Blits all surfaces onto the screen '''
        self.mouse_pos = mouse_pos
        if state != State.GAME:
            if self.win_anim_t < 1.0:
                self.win_anim_t += 0.04
                if self.win_anim_t > 1.0:
                    self.win_anim_t = 1.0
        else:
            self.win_anim_t = 0.0
        
        self.state = state
        # Clear background
        self.screen.fill(BACKGROUND_COLOUR)
        self.boardSurf.fill((0, 0, 0, 0))
        self.uiSurf.fill((0, 0, 0, 0))
        # Board surfaces
        self._render_board(board, tiles)
        self.screen.blit(self.boardSurf, self._get_board_pos())
        # UI surfaces
        self._render_ui(board.score, board.moves, state, restart_on_click, menu_on_click, events)
        self.screen.blit(self.uiSurf, self._get_ui_pos())            
    

    ########## =========== RENDER =========== ##########

    def _render_board(self, board: Board, tiles: list[Tile]):
        ''' Renders all board-related surfaces'''
        if self.state != State.MENU:
            self._render_board_base(board)
            self._render_board_tiles(tiles)
            if self.state != State.GAME:
                c1 = 0.5
                c3 = c1 + 1.0
                
                t = max(0.0, min(1.0, self.win_anim_t))
                lerp = 1.0 + c3 * ((t - 1.0) ** 3) + c1 * ((t - 1.0) ** 2)

                dark_overlay = pygame.Surface(self.boardSurf.get_size(), pygame.SRCALPHA)
                
                target_alpha = int(100 * lerp)
                clamped_alpha = max(0, min(100, target_alpha))
                
                pygame.draw.rect(
                    dark_overlay, 
                    (0, 0, 0, clamped_alpha), 
                    dark_overlay.get_rect(), 
                    border_radius=BOARD_ROUND
                )
                
                self.boardSurf.blit(dark_overlay, (0, 0))


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

    def _render_ui(self, score: int, moves: int, state: State, restart_on_click, menu_on_click, events) -> None:
        if state == State.MENU:
            self._render_menu(restart_on_click)
        elif state == State.WIN or state == State.LOSE:
            self._render_win(score, moves, restart_on_click, menu_on_click, events)
        elif state == State.GAME:
            ''' Renders all ui-related surfaces''' 
            # Render individual surfaces
            self.uiObjects["score"].render(score)
            self.uiObjects["highscore"].render(HIGHSCORE)
            # Blit individual surfaces onto main surf
            for name in self.uiObjects.keys():
                self.uiSurf.blit(self.uiObjects[name].surf, self.uiObjects[name].pos)
    
    def _render_win(self, score: int, moves: int, restart_on_click, menu_on_click, events: list[pygame.Event]) -> None:
        gameOverText = self.gameOverFont.render("Game Over", True, (156, 137, 121))
        scoreText = self.scoreFont.render(f"{score} points scored in {moves} moves.", True, (156, 137, 121))
        restartText = self.restartTextFont.render("Play Again", True, (156, 137, 121))
        menuText = self.restartTextFont.render("Menu", True, BACKGROUND_COLOUR)

        button_x = 250
        button_y = 50

        gameOver_y = -50
        gameOver_Target_y = 50
        
        score_start_y = -50
        score_target_y = 150

        restart_start_y = -50
        restart_target_y = 280

        menu_start_y = -50
        menu_target_y = 220

        self.restartSurf = pygame.Surface((button_x, button_y), pygame.SRCALPHA)
        pygame.draw.rect(self.restartSurf, BACKGROUND_COLOUR, (0, 0, button_x, button_y), border_radius=15)
        pygame.draw.rect(self.restartSurf, SCORE_BGCOLOUR, (0, 0, button_x, button_y), border_radius=15, width=5)
        self.restartSurf.blit(restartText, (65, 5))
        
        menuButtonSurf = pygame.Surface((button_x, button_y), pygame.SRCALPHA)
        pygame.draw.rect(menuButtonSurf, SCORE_COLOUR_SCORE, (0, 0, button_x, button_y), border_radius=15)
        menuTextRect = menuText.get_rect()
        menuTextRect.center = (button_x/2, button_y/2)
        menuButtonSurf.blit(menuText, menuTextRect)


        mouse_pos = self.mouse_pos
        mouse_clicked = pygame.mouse.get_pressed()[0]
        restart_is_hovered = pygame.Rect(SCREEN_SIZE.w/2 - button_x/2, restart_target_y - button_y/2, button_x, button_y).collidepoint(mouse_pos)
        menu_is_hovered = pygame.Rect(SCREEN_SIZE.w/2 - button_x/2, menu_target_y - button_y/2, button_x, button_y).collidepoint(mouse_pos)

        if restart_is_hovered:
            tint = pygame.Surface((button_x, button_y), pygame.SRCALPHA)
            
            pygame.draw.rect(
                tint, 
                (230, 230, 230, 255), 
                (0, 0, button_x, button_y), 
                border_radius=15
            )
            
            self.restartSurf.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        elif menu_is_hovered:
            tint = pygame.Surface((button_x, button_y), pygame.SRCALPHA)
            
            pygame.draw.rect(
                tint, 
                (230, 230, 230, 255), 
                (0, 0, button_x, button_y), 
                border_radius=15
            )
            
            menuButtonSurf.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        if restart_is_hovered and mouse_clicked:
            restart_on_click()
        elif menu_is_hovered and mouse_clicked:
            menu_on_click()
        

        self.screen.blit(*animate(self.win_anim_t, gameOverText, (SCREEN_SIZE.w / 2, gameOver_y), (SCREEN_SIZE.w / 2, gameOver_Target_y)))
        self.screen.blit(*animate(self.win_anim_t, scoreText, (SCREEN_SIZE.w / 2, score_start_y), (SCREEN_SIZE.w / 2, score_target_y)))
        self.screen.blit(*animate(self.win_anim_t, self.restartSurf, (SCREEN_SIZE.w / 2, restart_start_y), (SCREEN_SIZE.w / 2, restart_target_y)))
        self.screen.blit(*animate(self.win_anim_t, menuButtonSurf, (SCREEN_SIZE.w / 2, menu_start_y), (SCREEN_SIZE.w / 2, menu_target_y)))
        
        if not self.saved:
            self._render_dialog(events, score)

    def _render_menu(self, on_click):
        titleText = self.gameOverFont.render("2048", True, (156, 137, 121))
        scoreText = self.scoreFont.render(f"Try to get to 2048 to win!", True, (156, 137, 121))
        startText = self.restartTextFont.render("Start", True, (156, 137, 121))

        startButton_x = 250
        startButton_y = 50

        title_y = -50
        title_Target_y = 300
        
        score_start_y = -50
        score_target_y = 400

        start_start_y = -50
        start_target_y = 470

        left_col = 230

        self.startSurf = pygame.Surface((startButton_x, startButton_y), pygame.SRCALPHA)
        pygame.draw.rect(self.startSurf, BACKGROUND_COLOUR, (0, 0, startButton_x, startButton_y), border_radius=15)
        pygame.draw.rect(self.startSurf, SCORE_BGCOLOUR, (0, 0, startButton_x, startButton_y), border_radius=15, width=5)
        startTextRect = startText.get_rect()
        startTextRect.center = (startButton_x/2, startButton_y/2)
        self.startSurf.blit(startText, startTextRect)

        mouse_pos = self.mouse_pos
        mouse_clicked = pygame.mouse.get_pressed()[0]
        is_hovered = pygame.Rect(SCREEN_SIZE.w/2 - startButton_x/2 - left_col, start_target_y - startButton_y/2, startButton_x, startButton_y).collidepoint(mouse_pos)

        if is_hovered:
            tint = pygame.Surface((startButton_x, startButton_y), pygame.SRCALPHA)
            
            pygame.draw.rect(
                tint, 
                (230, 230, 230, 255), 
                (0, 0, startButton_x, startButton_y), 
                border_radius=15
            )
            
            self.startSurf.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        if is_hovered and mouse_clicked:
            on_click()
        

        self.screen.blit(*animate(self.win_anim_t, titleText, (SCREEN_SIZE.w / 2 - left_col, title_y), (SCREEN_SIZE.w / 2 - left_col, title_Target_y)))
        self.screen.blit(*animate(self.win_anim_t, scoreText, (SCREEN_SIZE.w / 2 - left_col, score_start_y), (SCREEN_SIZE.w / 2 - left_col, score_target_y)))
        self.screen.blit(*animate(self.win_anim_t, self.startSurf, (SCREEN_SIZE.w / 2 - left_col, start_start_y), (SCREEN_SIZE.w / 2 - left_col, start_target_y)))
        self._render_leaderboard()

    def _render_leaderboard(self):
        leaderboardText = self.leaderboardFont.render(f"LEADERBOARD", True, (156, 137, 121))
        
        leaderboard_start_y = -50
        leaderboard_target_y = 300

        right_col = 200

        self.screen.blit(*animate(self.win_anim_t, leaderboardText, (SCREEN_SIZE.w / 2 + right_col, leaderboard_start_y), (SCREEN_SIZE.w / 2 + right_col, leaderboard_target_y)))
        dividerSurface = pygame.Surface((800, 5), pygame.SRCALPHA)
        pygame.draw.rect(dividerSurface, (156, 137, 121), (0, 0, 350, 5))
        self.screen.blit(*animate(self.win_anim_t, dividerSurface, (SCREEN_SIZE.w / 2-200 + right_col, leaderboard_start_y), (SCREEN_SIZE.w / 2-200 + right_col+25, leaderboard_target_y+50), centered=1))
        for i in range(len(self.leaderboard)):
            text = self.leaderboardFont.render(f"#{i+1:<4}{self.leaderboard[i][0]:<10}", True, (156, 137, 121))
            score = self.leaderboardFont.render(f"{self.leaderboard[i][1]}", True, (156, 137, 121))
            self.screen.blit(*animate(self.win_anim_t, text, (SCREEN_SIZE.w / 2-150 + right_col, leaderboard_start_y), (SCREEN_SIZE.w / 2-150 + right_col, leaderboard_target_y+70+i*50), centered=1))
            self.screen.blit(*animate(self.win_anim_t, score, (SCREEN_SIZE.w / 2+150 + right_col, leaderboard_start_y), (SCREEN_SIZE.w / 2+150 + right_col, leaderboard_target_y+70+i*50), centered=2))
            self.screen.blit(*animate(self.win_anim_t, score, (SCREEN_SIZE.w / 2+150 + right_col, leaderboard_start_y), (SCREEN_SIZE.w / 2+150 + right_col, leaderboard_target_y+70+i*50), centered=2))

    def _render_dialog(self, events: list[pygame.Event], score: int):
        field_x = 250
        field_y = 50
        field_target_y = 70
        
        submitButton_x = 250
        submitButton_y = 50

        dialog_x = 400
        dialog_y = 300

        dialog_start_y = -50
        dialog_target_y = 500
        
        submit_target_y = 150

        title_y = 30

        title = self.titleFont.render("Enter your name!", True, BACKGROUND_COLOUR)
        submitText = self.leaderboardFont.render(f"Submit", True, (156, 137, 121))

        self.dialogSurf = pygame.Surface((dialog_x, dialog_y), pygame.SRCALPHA)
        absoluteFieldRect = pygame.Rect(SCREEN_SIZE.w/2 - field_x/2, dialog_target_y-dialog_y/2+field_target_y, field_x, field_y)
        pygame.draw.rect(self.dialogSurf, (156, 137, 121), (0, 0, dialog_x, dialog_y), border_radius=20)
        pygame.draw.rect(self.dialogSurf, (234, 230, 218), (0, 0, dialog_x, dialog_y), border_radius=20, width=5)
        pygame.draw.rect(self.dialogSurf, BACKGROUND_COLOUR, (self.dialogSurf.width/2 - field_x/2, field_target_y, field_x, field_y), border_radius=5)
        pygame.draw.rect(self.dialogSurf, BACKGROUND_COLOUR, (self.dialogSurf.width/2 - submitButton_x/2, submit_target_y, submitButton_x, submitButton_y), border_radius=15)
        pygame.draw.rect(self.dialogSurf, SCORE_BGCOLOUR, (self.dialogSurf.width/2 - submitButton_x/2, submit_target_y, submitButton_x, submitButton_y), border_radius=15, width=5)
        submitTextRect = submitText.get_rect()
        submitTextRect.center = (self.dialogSurf.width/2, submit_target_y + submitButton_y/2)
        titleRect = title.get_rect()
        titleRect.center = (self.dialogSurf.width/2, title_y)
        self.dialogSurf.blit(title, titleRect)
        self.dialogSurf.blit(submitText, submitTextRect)

        mouse_pos = self.mouse_pos
        mouse_clicked = pygame.mouse.get_pressed()[0]
        is_hovered = pygame.Rect(SCREEN_SIZE.w/2 - submitButton_x/2, dialog_target_y-dialog_y/2+submit_target_y, submitButton_x, submitButton_y).collidepoint(mouse_pos)

        if is_hovered:
            tint = pygame.Surface((submitButton_x, submitButton_y), pygame.SRCALPHA)

            pygame.draw.rect(
                tint, 
                (230, 230, 230, 255), 
                (0, 0, submitButton_x, submitButton_y), 
                border_radius=15
            )
            
            self.dialogSurf.blit(tint, (self.dialogSurf.width/2 - submitButton_x/2, submit_target_y), special_flags=pygame.BLEND_RGBA_MULT)
        if mouse_clicked and is_hovered:
            self._save_score(self.fieldString, score)
            self.saved = True
            return

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if absoluteFieldRect.collidepoint(event.pos):
                    self.active = True
                else:
                    self.active = False
            if self.active: 
                if event.type == pygame.TEXTINPUT:
                    self.fieldString += event.text
            
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.fieldString = self.fieldString[:-1]

        inputText = self.scoreFont.render(self.fieldString, True, (156, 137, 121))
        inputTextRect = inputText.get_rect()
        inputTextRect.midleft = (self.dialogSurf.width/2 - field_x/2+ + 10, field_target_y+field_y/2)
        self.dialogSurf.blit(inputText, inputTextRect)
        self.screen.blit(*animate(self.win_anim_t, self.dialogSurf, (SCREEN_SIZE.w / 2, dialog_start_y), (SCREEN_SIZE.w / 2, dialog_target_y)))
        # pygame.draw.rect(self.screen, (255, 0, 0, 255), (SCREEN_SIZE.w/2 - submitButton_x/2, dialog_target_y-dialog_y/2+submit_target_y, submitButton_x, submitButton_y))

    def _save_score(self, name: str, score: int):
        player_exists = False
        for i, entry in enumerate(self.leaderboard):
            if name == entry[0]:
                if score > int(entry[1]):
                    self.leaderboard[i] = (name, score)
                player_exists = True
                break
        
        if not player_exists:
            self.leaderboard.append((name, score))
        self.leaderboard.sort(key=lambda entry: int(entry[1]), reverse=True)
        self.leaderboard = self.leaderboard[:5]

        data = ""
        for entry in self.leaderboard:
            data += f"{entry[0]},{entry[1]}\n"

        with open("./best.txt", "w") as file:
            file.write(data)

    def _get_textSurface(self, value: int) -> pygame.Surface:
        ''' Renders the number surface of tiles'''
        if value not in self.fontSurfaces:
            self.fontSurfaces[value] = self.fontDefault.render(str(value), True, TILE_TEXT_COLOURS["default"])
        return self.fontSurfaces[value]
    
    ########## ====== POSITION & SIZE ======= ##########

    def resize(self, board: Board) -> None:
        self._resize_board(board.rows, board.cols)

    def _resize_board(self, rows: int, cols: int) -> None:
        self.boardSurf = pygame.Surface(self._get_board_size(rows, cols), pygame.SRCALPHA)

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
    