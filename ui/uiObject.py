from   collections.abc import Callable

import pygame

from   constants        import *
from   utils.namedpair  import Size
from   utils.vector     import Vector


def _centerRect(
        selfSize: tuple[int, int],
        otherRect: pygame.Rect | tuple[int, int, int, int]
    ) -> pygame.Rect:

    centeredRect = pygame.Rect(0, 0, *selfSize)
    centeredRect.center = pygame.Rect(otherRect).center
    return centeredRect


class UIObject:
    def __init__(self,
            size: Size,
            pos:  Vector | tuple[Vector, Vector]
            ) -> None:
        
        self.surface = pygame.Surface(size, pygame.SRCALPHA)

        self.size = Size(size)
        self.animation_sPos = Vector(pos) if type(pos) == Vector else Vector(pos[0])
        self.animation_ePos = Vector(pos) if type(pos) == Vector else Vector(pos[1])
        self.pos            = self.animation_sPos

    def render(self) -> None:
        ...

class UIRect(UIObject):
    def __init__(self,
            size: Size,
            pos:  Vector | tuple[Vector, Vector],
            colour:       tuple[int, int, int],
            borderRad:    int,
            borderWidth:  int                  = 0,
            borderColour: tuple[int, int, int] = (0, 0, 0)
            ) -> None:
        
        super().__init__(size, pos)

        self.colour       = colour
        self.borderRad    = borderRad
        self.borderWidth  = borderWidth
        self.borderColour = borderColour

    def render(self) -> None:
        # Rectangle
        pygame.draw.rect(self.surface, self.colour, (0, 0, *self.size.to_int()), border_radius=self.borderRad)
        # Border
        if self.borderWidth != 0:
            pygame.draw.rect(self.surface, self.borderColour, (0, 0, *self.size.to_int()), width=self.borderWidth, border_radius=self.borderRad)

class UIScore(UIRect):
    def __init__(self,
            size:   Size,
            pos:    Vector | tuple[Vector, Vector],
            text:   str,
            border: bool = False
            ) -> None:
        
        if border:
            super().__init__(size, pos, SCORE_BGCOLOUR, borderRad=15, borderWidth=2, borderColour=SCORE_OUTCOLOUR)
        else:
            super().__init__(size, pos, SCORE_OUTCOLOUR, borderRad=15)

        self.title = text

        self.titleFont = pygame.font.Font(FONT_FILENAME, 15)
        self.scoreFont = pygame.font.Font(FONT_FILENAME, 30)

    def render(self, score: int) -> None:
        
        super().render()
        # print(f"Rendered score's background")

        # Cache text surfaces
        title_surf = self.titleFont.render(self.title, True, SCORE_COLOUR_TITLE)
        score_surf = self.scoreFont.render(str(score), True, SCORE_COLOUR_SCORE)
        # Title
        self.surface.blit(
            title_surf,
            _centerRect(
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
        self.surface.blit(
            score_surf,
            _centerRect(
                score_surf.get_size(),
                (
                    0,
                    self.size.h * 0.3,
                    self.size.w,
                    self.size.h * 0.6
                )
            )
        )

class UIText(UIObject):
    def __init__(self,
            size:   Size,
            pos:    Vector | tuple[Vector, Vector],
            text:   str,
            font:   pygame.font.Font,
            colour: tuple[int, int, int] = (0, 0, 0)
            ) -> None:
        
        super().__init__(size, pos)

        # Cached font surface
        self.fontSurface = font.render(text, True, colour)

    def render(self) -> None:
        self.surface.blit(self.fontSurface, self.pos.to_int())

# class UITextbox(UIRect, UIText):
#     def __init__(self,
#             size:   Size,
#             pos:    Vector | tuple[Vector, Vector],
#             text:   str,
#             font:   pygame.font.Font,
#             textColour: tuple[int, int, int] = (0, 0, 0),
#             colour:       tuple[int, int, int],
#             borderRad:    int,
#             borderWidth:  int                  = 0,
#             borderColour: tuple[int, int, int] = (0, 0, 0)
#             ) -> None:
        
#         super()

class UIbutton(UIRect):
    def __init__(self,
            size: Size,
            pos:  Vector | tuple[Vector, Vector],
            onClick: Callable,
            text:         str,
            colour:       tuple[int, int, int],
            borderColour: tuple[int, int, int]
            ) -> None:
        
        super().__init__(size, pos, colour, borderRad=15, borderWidth=2, borderColour=borderColour)

        self.onClick = onClick

    def render(self) -> None:
        ...