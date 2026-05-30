import pygame

DIRECTION_KEYS = {
    pygame.K_LEFT   : "left",
    pygame.K_a      : "left",
    pygame.K_RIGHT  : "right",
    pygame.K_d      : "right",
    pygame.K_UP     : "up",
    pygame.K_w      : "up",
    pygame.K_DOWN   : "down",
    pygame.K_s      : "down",

    pygame.K_r      : "newGame",
}

def get_action(events: list) -> str | None:
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key in DIRECTION_KEYS:
                return DIRECTION_KEYS[event.key]
    return None