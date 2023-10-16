import pygame
from . import constants as C
from . import tools
import os

pygame.init()
pygame.event.set_allowed([pygame.KEYDOWN, pygame.KEYUP, pygame.QUIT])
pygame.display.set_caption(C.CAPTION)
SCREEN = pygame.display.set_mode(C.SCREEN_SIZE)
# SCREEN_RECT = SCREEN.get_rect()

GRAPHICS = tools.load_graphics(os.path.join('resources', 'graphics'))
MUSICS = tools.load_musics(os.path.join('resources', 'music'))
SOUNDS = tools.load_sounds(os.path.join('resources', 'sound'))
