import pygame
import math

width,height=800,600
screen=pygame.display.set_mode((width,height))

clock=pygame.time.Clock()

running=True

while running:
    for evt in pygame.event.get():
        if evt.type==pygame.QUIT:
            running=False
                       
    mx,my=pygame.mouse.get_pos()
    mb=pygame.mouse.get_pressed()
    
    clock.tick(60)
    pygame.display.flip()
            
quit()