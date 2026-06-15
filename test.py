import pygame

# Initialize modules
pygame.init()
screen = pygame.size = pygame.display.set_mode((640, 480))
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

# Input box settings
input_box = pygame.Rect(150, 200, 340, 45)
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
color = color_inactive

# State variables
user_text = ""
active = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # 1. Toggle focus when clicking the input box
        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_box.collidepoint(event.pos):
                active = True
            else:
                active = False
            color = color_active if active else color_inactive

        # 2. Capture regular typing (only when box is active)
        if active and event.type == pygame.TEXTINPUT:
            user_text += event.text

        # 3. Capture special commands like Backspace and Enter
        if active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                user_text = user_text[:-1]
            elif event.key == pygame.K_RETURN:
                print(f"Submitted text: {user_text}")
                user_text = ""  # Clear the box

    # Drawing steps
    screen.fill((30, 30, 30))

    # Render text surface
    text_surface = font.render(user_text, True, (255, 255, 255))
    
    # Dynamically expand the box size if text gets too long
    input_box.w = max(340, text_surface.get_width() + 20)

    # Blit text and draw box outline
    screen.blit(text_surface, (input_box.x + 10, input_box.y + 10))
    pygame.draw.rect(screen, color, input_box, 2)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
