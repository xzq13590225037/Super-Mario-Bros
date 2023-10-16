import pygame
from .. import setup, tools
from .. import constants as C


class Coin(pygame.sprite.Sprite):

    frame_rect_list = [(52, 113, 8, 14), (4, 113, 8, 14), (20, 113, 8, 14), (36, 113, 8, 14)]

    def __init__(self, x, y, frame_rect_list=frame_rect_list):
        pygame.sprite.Sprite.__init__(self)
        self.frames = []
        self.frame_index = 0
        self.load_frames(frame_rect_list)
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y - 5 #？？？-5
        self.gravity = 1
        self.y_vel = -15
        self.animation_timer = 0
        self.initial_height = self.rect.bottom - 5 #?


    def load_frames(self, frame_rect_list):
        sheet = setup.GRAPHICS['item_objects']

        for frame_rect in frame_rect_list:
            self.frames.append(tools.get_image(sheet, *frame_rect, (0,0,0), C.BRICK_SIZE_MULTIPLIER))

    def update(self, game_info):
        self.current_time = game_info[C.CURRENT_TIME]
        self.spinning()

    def spinning(self):
        self.image = self.frames[self.frame_index]
        self.rect.y += self.y_vel #?
        self.y_vel += self.gravity

        if self.current_time - self.animation_timer > 80:
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 0
            self.animation_timer = self.current_time

        if self.rect.bottom > self.initial_height:
            self.kill()


class StaticCoin(Coin):
    def __init__(self, x, y):
        frame_rect_list = [(3, 98, 9, 13), (19, 98, 9, 13), (35, 98, 9, 13), (51, 98, 9, 13)]
        Coin.__init__(self, x, y, frame_rect_list)

    def update(self, game_info):
        self.current_time = game_info[C.CURRENT_TIME]
        dur_list = [375, 125, 125, 125]

        if self.animation_timer == 0:
            self.animation_timer = self.current_time
        elif self.current_time - self.animation_timer > dur_list[self.frame_index]:
            self.frame_index += 1
            if self.frame_index == 4:
                self.frame_index = 0
            self.animation_timer = self.current_time

        self.image = self.frames[self.frame_index]

class FlashingCoin(Coin):
    def __init__(self, x, y):
        frame_rect_list = [(1, 160, 5, 8), (9, 160, 5, 8),
                        (17, 160, 5, 8), (9, 160, 5, 8)]
        Coin.__init__(self, x, y, frame_rect_list)
        self.rect.x = x
        self.rect.y = y

    def update(self, game_info):
        self.current_time = game_info[C.CURRENT_TIME]
        dur_list = [375, 125, 125, 125]

        if self.animation_timer == 0:
            self.animation_timer = self.current_time
        elif self.current_time - self.animation_timer > dur_list[self.frame_index]:
            self.frame_index += 1
            if self.frame_index == 4:
                self.frame_index = 0
            self.animation_timer = self.current_time

        self.image = self.frames[self.frame_index]
