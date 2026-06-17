from    collections.abc  import Callable
from    functools        import wraps

import  pygame

from    constants        import *
from    utils.namedpair  import Size
from    utils.vector     import Vector
from    ui.inputHandler  import InputState


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
    def _wrapper_init(method):
        @wraps(method)

        def wrapper(self, *args, **kwargs) -> None:
            method(self, *args, **kwargs)
            # Render a copy for references (i.e. UIButton.iconSurface)
            self.render(None)

        return wrapper

    @staticmethod
    def _wrapper_render(method):
        @wraps(method)

        def wrapper(self, dest: pygame.Surface | None = None, *args, **kwargs) -> None:
            # Clear background
            self.surface.fill((0, 0, 0, 0))
            # Render surface
            method(self, dest, *args, **kwargs)
            # Efficiency
            self.surface = self.surface.convert_alpha()
            # Blit surface to dest
            if dest is not None:
                dest.blit(self.surface, self.pos)

        return wrapper

    def render(self, dest: pygame.Surface | None = None) -> None:
        ''' Renders the UIObject's surface '''
        ...

class UIRect(UIObject):
    @UIObject._wrapper_init
    def __init__(self,
            size: Size,
            pos:  Vector | tuple[Vector, Vector],
            bgColour:     tuple[int, int, int] | tuple[int, int, int, int],
            borderRad:    int,
            borderWidth:  int                  = 0,
            borderColour: tuple[int, int, int] | tuple[int, int, int, int] = (0, 0, 0),
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
    
    @UIObject._wrapper_init
    def __init__(self,
            size:    Size,
            pos:     Vector | tuple[Vector, Vector],
            text:    str,
            font:    pygame.font.Font,
            colour:  tuple[int, int, int] | tuple[int, int, int, int],
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
            self._alignShift()
        self.surface.blit(self.fontSurface, self.posShift.to_int())

class UITextbox(UIRect, UIText):
    @UIObject._wrapper_init
    def __init__(self,
            size:           Size,
            pos:            Vector | tuple[Vector, Vector],
            text:           str,
            font:           pygame.font.Font,
            colour:         tuple[int, int, int] | tuple[int, int, int, int],
            align:          str,
            bgColour:       tuple[int, int, int] | tuple[int, int, int, int],
            borderRad:      int,
            borderWidth:    int                  = 0,
            borderColour:   tuple[int, int, int] | tuple[int, int, int, int] = (0, 0, 0),
            **kwargs
            ) -> None:
        
        UIObject.__init__(self, size, pos)

        self.rectObj = UIRect(
            size         = size,
            pos          = Vector(0, 0),
            bgColour     = bgColour,
            borderRad    = borderRad,
            borderWidth  = borderWidth,
            borderColour = borderColour,
        )

        self.textObj = UIText(
            size   = size,
            pos    = Vector(0, 0),
            text   = text,
            font   = font,
            colour = colour,
            align  = align,
        )

    @UIObject._wrapper_render
    def render(self, dest: pygame.Surface | None = None) -> None:
        self.rectObj.render(self.surface)
        self.textObj.render(self.surface)

class UIScore(UIRect, UIText):
    @UIObject._wrapper_init
    def __init__(self,
            size:           Size,
            pos:            Vector | tuple[Vector, Vector],
            getValue:       Callable[[], int],
            title:          str,
            titleColour:    tuple[int, int, int] | tuple[int, int, int, int],
            scoreColour:    tuple[int, int, int] | tuple[int, int, int, int],
            bgColour:       tuple[int, int, int] | tuple[int, int, int, int],
            borderWidth:    int = 0,
            borderColour:   tuple[int, int, int] | tuple[int, int, int, int] = (0, 0, 0),
            **kwargs
            ) -> None:

        UIObject.__init__(self, size=size, pos=pos)

        self.rectObj = UIRect(
            size         = size,
            pos          = Vector(0, 0),
            bgColour     = bgColour, 
            borderRad    = 15,
            borderWidth  = borderWidth, 
            borderColour = borderColour,
        )

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

        self.getValue = getValue

    @UIObject._wrapper_render
    def render(self, dest: pygame.Surface | None = None) -> None:
        # Background
        self.rectObj.render(self.surface)
        # Text
        self.scoreObj.text = str(self.getValue())
        self.titleObj.render(self.surface)
        self.scoreObj.render(self.surface)

class UIButton(UIObject):
    @UIObject._wrapper_init
    def __init__(self,
            size:        Size,
            pos:         Vector | tuple[Vector, Vector],
            onClick:     Callable,
            iconSurface: pygame.Surface,
            **kwargs
            ) -> None:

        UIObject.__init__(self, size, pos)

        self.iconSurface = iconSurface

        self.hover:   bool = False
        self.clicked: bool = False
        self.onClick = onClick

        self.hoverOverlay = pygame.Surface(self.size, pygame.SRCALPHA)
        self.clickOverlay = pygame.Surface(self.size, pygame.SRCALPHA)
        self.hoverOverlay.fill((255, 255, 255, 200))
        self.clickOverlay.fill((225, 225, 225, 255))

    @UIObject._wrapper_render
    def render(self, dest: pygame.Surface | None = None) -> None:
        # Background
        self.surface.blit(self.iconSurface, (0, 0))
        # Overlays
        if self.clicked:
            self.surface.blit(self.clickOverlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        elif self.hover:
            self.surface.blit(self.hoverOverlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)


class UIManager:
    def __init__(self, objs: list[UIObject] = []) -> None:
        self.staticObjs:  list[UIObject] = []
        self.dynamicObjs: list[UIButton] = []
        # Add initialized objects
        for obj in objs:
            self.addUIObject(obj)

    def addUIObject(self, obj: UIObject) -> None:
        if isinstance(obj, (UIButton)):
            self.dynamicObjs.append(obj)
        else:
            self.staticObjs.append(obj)

    def update(self, inputState: InputState) -> None:
        for obj in self.dynamicObjs:
            if isinstance(obj, UIButton):
                self._update_button(obj, inputState)

    def _update_button(self, button: UIButton, inputState: InputState) -> None:
        # Mouse on top of button
        if self._coerce_rect_UIObject(button).collidepoint(inputState.mousePos.to_tuple()):
            button.hover = True
            # Update cursor
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            # Mouse clicked
            if inputState.mouseButtons_up["left"] and not button.clicked:
                button.clicked = True
                button.onClick()
                # Update cursor
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            # Mouse not clicked
            else:
                button.clicked = False
        # Mouse not on top of button
        else:
            button.hover = False
            # Update cursor
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def _coerce_rect_UIObject(self, obj: UIObject) -> pygame.Rect:
        return pygame.Rect(obj.pos.to_tuple(), obj.surface.get_size())
