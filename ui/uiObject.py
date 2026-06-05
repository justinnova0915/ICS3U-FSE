from   collections.abc import Iterable

import pygame

from   constants import *


def centerRect(
        selfRect:  pygame.Rect | tuple[int, int, int, int],
        otherRect: pygame.Rect | tuple[int, int, int, int]
    ) -> pygame.Rect:

    centeredRect = pygame.Rect(selfRect)
    centeredRect.center = pygame.Rect(otherRect).center
    return centeredRect


class uiObject:
    def __init__(self, size: tuple[int, int] | Size):
        self.size : Size
        self.surf : pygame.Surface
        self.resize(size)

    def resize(self, size: tuple[int, int] | Size) -> None:
        self.size = Size(*size)
        self.surf = pygame.Surface(size, pygame.SRCALPHA)

    def render(self) -> None:
        ...

class uiScore(uiObject):
    def __init__(self, size: tuple[int, int] | Size, title: str):
        super().__init__(size)
        self.title = title

        self.titleFont = pygame.font.Font(FONT_FILENAME, 10)
        self.scoreFont = pygame.font.Font(FONT_FILENAME, 24)

    def render(self, score: int) -> None:
        title_surf = self.titleFont.render(self.title, True, SCORE_COLOUR_TITLE)
        score_surf = self.scoreFont.render(str(score), True, SCORE_COLOUR_SCORE)

        pygame.draw.rect(self.surf, SCORE_BGCOLOUR, (0, 0, *self.size), border_radius=int(min(self.size) * 0.2))
        self.surf.blit(
            title_surf,
            centerRect(
                title_surf.get_rect(),
                (
                    0,
                    0,
                    self.size.w,
                    self.size.h * 0.2
                )
            )
        )
        self.surf.blit(
            score_surf,
            centerRect(
                score_surf.get_rect(),
                (
                    0,
                    self.size.h * 0.2,
                    self.size.w,
                    self.size.h * 0.8
                )
            )
        )