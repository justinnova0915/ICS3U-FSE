import pygame
import constants

def animate(t: float, text: pygame.Surface, start: tuple[float, float], end: tuple[float, float], centered:int=0) -> tuple[pygame.Surface, pygame.Rect]:
        
    c1 = 0.5
    c3 = c1 + 1.0
    lerp = 1.0 + c3 * ((t - 1.0) ** 3) + c1 * ((t - 1.0) ** 2)
    current_alpha = max(0, min(255, int(0 + (255 - 0) * lerp)))
    
    text.set_alpha(current_alpha)

    textRect = text.get_rect()

    curTextPos = (
        start[0] + (end[0] - start[0]) * lerp,
        start[1] + (end[1] - start[1]) * lerp 
    )

    if centered == 0:
        textRect.center = curTextPos
    elif centered == 1:
        textRect.topleft = curTextPos
    elif centered == 2:
        textRect.topright = curTextPos


    return (text, textRect)