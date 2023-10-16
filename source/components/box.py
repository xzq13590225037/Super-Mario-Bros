import pygame
from .. import setup, tools
from .. import constants as C
from .powerup import create_powerup
from .coin import Coin

class Box(pygame.sprite.Sprite):
    def __init__(self, data, group=None, name=C.MAP_BOX):
        pygame.sprite.Sprite.__init__(self)
        self.frames = []
        self.frame_index = 0
        self.load_frames()
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = data['x']
        self.rect.y = data['y']

        self.rest_height = self.rect.y
        self.first_half = True
        self.animation_timer = 0
        self.state = C.RESTING
        self.y_vel = 0
        self.gravity = 1.2
        self.type = data['type']
        self.group = group
        self.name = name

    def load_frames(self):
        frame_rect_list = [(384, 0, 16, 16), (400, 0, 16, 16),
                           (416, 0, 16, 16), (400, 0, 16, 16), (432, 0, 16, 16)]
        for frame_rect in frame_rect_list:
            self.frames.append(tools.get_image(setup.GRAPHICS['tile_set'], *frame_rect, (0,0,0), C.BRICK_SIZE_MULTIPLIER))

    def update(self, game_info):
        self.current_time = game_info[C.CURRENT_TIME]
        if self.state == C.RESTING:
            self.resting()

        elif self.state == C.BUMPED:
            self.bumped(game_info)

    def bumped(self, game_info):
        self.rect.y += self.y_vel
        self.y_vel += self.gravity

        if self.rect.y > self.rest_height + 5: # 为了更加逼真
            self.rect.y = self.rest_height
            self.state = C.OPENED
            if self.type == C.TYPE_COIN:
                setup.SOUNDS['coin'].play()
                self.group.add(Coin(self.rect.centerx, self.rect.y)) # 一会处理
            else:
                setup.SOUNDS['powerup_appears'].play()
                self.group.add(create_powerup(self.rect.centerx, self.rect.y, self.type, game_info))
        self.frame_index = 4
        self.image = self.frames[self.frame_index]

    def start_bump(self):
        self.y_vel = -6
        self.state = C.BUMPED


    def resting(self):
        dur_list = [375, 125, 125, 125]
        if self.current_time - self.animation_timer > dur_list[self.frame_index]:
            self.frame_index += 1
            if self.frame_index == 4:
                self.frame_index = 0
            self.animation_timer = self.current_time
        self.image = self.frames[self.frame_index]