from    collections.abc  import Callable
from    functools        import wraps

import  pygame

from    constants        import *
from    utils.namedpair  import Size
from    utils.vector     import Vector


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

    @staticmethod
    def _wrapper_render(method):
        @wraps(method)

        def wrapper(self, dest: pygame.Surface | None = None, *args, **kwargs) -> None:
            method(self, dest, *args, **kwargs)
            if dest is not None:
                dest.blit(self.surface, self.pos)

        return wrapper

    @_wrapper_render
    def render(self, dest: pygame.Surface | None = None) -> None:
        ''' Renders the UIObject's surface '''
        ...

class UIRect(UIObject):
    def __init__(self,
            size: Size,
            pos:  Vector | tuple[Vector, Vector],
            bgColour:     tuple[int, int, int],
            borderRad:    int,
            borderWidth:  int                  = 0,
            borderColour: tuple[int, int, int] = (0, 0, 0),
            **kwargs
            ) -> None:
        
        UIObject.__init__(self, size, pos, **kwargs)

        self.colour       = bgColour
        self.borderRad    = borderRad
        self.borderWidth  = borderWidth
        self.borderColour = borderColour

    @UIObject._wrapper_render
    def render(self, dest: pygame.Surface | None = None) -> None:
        # Rectangle
        pygame.draw.rect(self.surface, self.colour, (0, 0, *self.size.to_int()), border_radius=self.borderRad)
        # Border
        if self.borderWidth != 0:
            pygame.draw.rect(self.surface, self.borderColour, (0, 0, *self.size.to_int()), width=self.borderWidth, border_radius=self.borderRad)

class UIText(UIObject):
    def _alignShift(self) -> None:
        match self.alignment:
            case 'c':
                self.posShift = Vector(self.size - self.fontSurface.get_size()) // 2
            case 'l':
                self.posShift = Vector(0, (self.size.h - self.fontSurface.get_height()) // 2)
            case 'r':
                self.posShift = Vector(self.size.w - self.fontSurface.get_width(), (self.size.h - self.fontSurface.get_height()) // 2)
            case 't':
                self.posShift = Vector((self.size.w - self.fontSurface.get_width()) // 2, 0)
            case 'b':
                self.posShift = Vector((self.size.w - self.fontSurface.get_width()) // 2, self.size.h - self.fontSurface.get_height())
            case _:
                self.posShift = Vector(0, 0)

    def __init__(self,
            size:    Size,
            pos:     Vector | tuple[Vector, Vector],
            text:    str,
            font:    pygame.font.Font,
            colour:  tuple[int, int, int],
            align:   str  = '',
            dynamic: bool = False,
            **kwargs
            ) -> None:
        
        UIObject.__init__(self, size, pos, **kwargs)

        self.text        = text
        self.font        = font
        self.colour      = colour
        self.fontSurface = self.font.render(self.text, True, self.colour)
        self.dynamic = dynamic # Dynamic text (e.g. score)

        self.alignment = align
        self.posShift  = Vector(0, 0) # Pos shift for centering etc.
        self._alignShift()

    @UIObject._wrapper_render
    def render(self, dest: pygame.Surface | None = None) -> None:
        if self.dynamic:
            self.fontSurface = self.font.render(self.text, True, self.colour)
        self.surface.blit(self.fontSurface, (self.pos + self.posShift).to_int())

class UITextbox(UIRect, UIText):
    def __init__(self,
            size:           Size,
            pos:            Vector | tuple[Vector, Vector],
            text:           str,
            font:           pygame.font.Font,
            colour:         tuple[int, int, int],
            alignment:      str,
            bgColour:       tuple[int, int, int],
            borderRad:      int,
            borderWidth:    int                  = 0,
            borderColour:   tuple[int, int, int] = (0, 0, 0),
            **kwargs
            ) -> None:
        
        super().__init__(
            size         = size,
            pos          = pos,
            text         = text,
            font         = font,
            colour       = colour,
            alignment    = alignment,
            bgColour     = bgColour,
            borderRad    = borderRad,
            borderWidth  = borderWidth,
            borderColour = borderColour,
            **kwargs
        )     

    @UIObject._wrapper_render
    def render(self, dest: pygame.Surface | None = None) -> None:
        UIRect.render(self, dest)
        UIText.render(self, dest)

class UIScore(UIRect, UIText):

    def __init__(self,
            size:           Size,
            pos:            Vector | tuple[Vector, Vector],
            title:          str,
            titleColour:    tuple[int, int, int],
            scoreColour:    tuple[int, int, int],
            bgColour:       tuple[int, int, int],
            borderWidth:    int                  = 0,
            borderColour:   tuple[int, int, int] = (0, 0, 0),
            **kwargs
            ) -> None:

        # Initialize shared UIObject properties first
        UIObject.__init__(self, size=size, pos=pos)
        # Explicitly initialize UIRect
        self.rectObj = UIRect(
            size         = size,
            pos          = pos,
            bgColour     = bgColour, 
            borderRad    = 15,
            borderWidth  = borderWidth, 
            borderColour = borderColour,
        )
        # Explicitly initialize UIText
        self.titleObj = UIText(
            size    = Size(self.size.w, self.size.h * 0.4),
            pos     = Vector(0, 0),
            text    = title,
            font    = pygame.font.Font(FONT_FILENAME, 15),
            colour  = titleColour,
            align   ='c',
            dynamic = True
        )
        self.scoreObj = UIText(
            size    = Size(self.size.w, self.size.h * 0.6),
            pos     = Vector(0, self.size.h * 0.3),
            text    = title,
            font    = pygame.font.Font(FONT_FILENAME, 30),
            colour  = scoreColour,
            align   ='c',
            dynamic = True
        )

    @UIObject._wrapper_render
    def render(self, dest: pygame.Surface | None = None, score: int = -1) -> None:
        # Background
        self.rectObj.render(self.surface)
        # Text
        self.scoreObj.text = str(score)
        self.titleObj.render(self.surface)
        self.scoreObj.render(self.surface)
        # DEBUG
        pygame.draw.rect(self.surface, (0, 255, 0), (0, 0, *self.size), 2)

class UIbutton(UIRect):
    def __init__(self,
            size: Size,
            pos:  Vector | tuple[Vector, Vector],
            onClick: Callable,
            text:         str,
            colour:       tuple[int, int, int],
            borderColour: tuple[int, int, int],
            **kwargs
            ) -> None:
        
        super().__init__(
            size,
            pos,
            colour,
            borderRad=15,
            borderWidth=2,
            borderColour=borderColour,
            **kwargs
            )

        self.onClick = onClick

    @UIObject._wrapper_render
    def render(self, dest: pygame.Surface | None = None) -> None:
        ...

