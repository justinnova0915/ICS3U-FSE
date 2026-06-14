from   collections.abc import Iterable

import pygame

from   constants import *


def centerRect(
        selfSize: tuple[int, int],
        otherRect: pygame.Rect | tuple[int, int, int, int]
    ) -> pygame.Rect:

    centeredRect = pygame.Rect(0, 0, *selfSize)
    centeredRect.center = pygame.Rect(otherRect).center
    return centeredRect


class uiObject:
    def __init__(self, size: tuple[int, int] | Size, pos: tuple[int, int] | Coord):
        self.surf : pygame.Surface
        self.size : Size
        self.pos  : Coord
        self.transform(size, pos)

    def transform(self, size: tuple[int, int] | Size, pos: tuple[int, int] | Coord | None = None) -> None:
        self.surf = pygame.Surface(size, pygame.SRCALPHA)
        self.size = Size(*size)
        if pos is not None: self.pos = Coord(*pos)

    def render(self) -> None:
        ...

class uiScore(uiObject):
    def __init__(self, size: tuple[int, int] | Size, pos: tuple[int, int] | Coord, title: str, width: int=0):
        super().__init__(size, pos)
        self.title = title

        self.width     = width
        self.borderRad = 15

        self.titleFont = pygame.font.Font(FONT_FILENAME, 15)
        self.scoreFont = pygame.font.Font(FONT_FILENAME, 30)

    def render(self, score: int) -> None:
        # Cache text surfaces
        title_surf = self.titleFont.render(self.title, True, SCORE_COLOUR_TITLE)
        score_surf = self.scoreFont.render(str(score), True, SCORE_COLOUR_SCORE)

        # Background
        pygame.draw.rect(
            self.surf,
            SCORE_BGCOLOUR,
            (0, 0, *self.size),
            border_radius=self.borderRad
        )
        # Outline
        pygame.draw.rect(
            self.surf,
            SCORE_OUTCOLOUR,
            (0, 0, *self.size),
            border_radius=self.borderRad,
            width=self.width
        )
        # Title
        self.surf.blit(
            title_surf,
            centerRect(
                title_surf.get_size(),
                (
                    0,
                    self.size.h * 0,
                    self.size.w,
                    self.size.h * 0.4
                )
            )
        )
        # Score
        self.surf.blit(
            score_surf,
            centerRect(
                score_surf.get_size(),
                (
                    0,
                    self.size.h * 0.3,
                    self.size.w,
                    self.size.h * 0.6
                )
            )
        )