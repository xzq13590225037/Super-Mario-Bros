import pygame
from .. import tools, setup
from .. import constants as C


class Collider(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, name):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((w, h)).convert()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.name = name


class Stuff(pygame.sprite.Sprite):
    def __init__(self, x, y, sheet, image_rect_list, scale):
        pygame.sprite.Sprite.__init__(self)

        self.frames = []
        self.frame_index = 0
        for image_rect in image_rect_list:
            self.frames.append(tools.get_image(sheet, *image_rect, (0,0,0), scale))
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Pipe(Stuff):
    # 感觉这一段很没必要啊，既然背景里头都有管子了，没必要重画吧，直接拿坐标去判断是否可以进管子
    def __init__(self, x, y, width, height, type, name=C.MAP_PIPE):
        if type == C.PIPE_TYPE_HORIZONTAL:
            rect = [(32, 128, 37, 30)] # rect =  # 这两个尺寸有点迷
        else:
            rect = [(0, 160, 32, 30)]
        Stuff.__init__(self, x, y, setup.GRAPHICS['tile_set'], rect, C.BRICK_SIZE_MULTIPLIER)
        self.name = name
        self.type = type
        if type != C.PIPE_TYPE_HORIZONTAL: #?
            self.create_image(x, y, height)

    def create_image(self, x, y, pipe_height):
        img = self.image
        rect = self.image.get_rect()

        w = rect.w
        h = rect.h
        self.image = pygame.Surface((w, pipe_height)).convert()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        top_height = h//2 + 3
        bottom_height = h//2 - 3
        self.image.blit(img, (0, 0), (0, 0, w, top_height))
        num = (pipe_height - top_height) // bottom_height + 1
        for i in range(num):
            y = top_height + i * bottom_height
            self.image.blit(img, (0, y), (0, top_height, w, bottom_height))
        self.image.set_colorkey((0,0,0))


class Checkpoint(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, type, enemy_groupid=0, map_index=0, name=C.MAP_CHECKPOINT):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.type = type
        self.enemy_groupid = enemy_groupid
        self.map_index = map_index
        self.name = name

class Flag(Stuff):
    def __init__(self, x, y):
        Stuff.__init__(self, x, y, setup.GRAPHICS['item_objects'], [(128, 32, 16, 16)], C.SIZE_MULTIPLIER)
        self.state = C.TOP_OF_POLE
        self.y_vel = 5

    def update(self, *args):
        if self.state == C.SLIDE_DOWN:
            self.rect.y += self.y_vel
            if self.rect.bottom >= 485: # harding for now
                self.state = C.BOTTOM_OF_POLE

class Pole(Stuff):
    def __init__(self, x, y):
        Stuff.__init__(self, x, y, setup.GRAPHICS['tile_set'], [(263, 144, 2, 16)], C.BRICK_SIZE_MULTIPLIER)

class PoleTop(Stuff):
    def __init__(self, x, y):
        Stuff.__init__(self, x, y, setup.GRAPHICS['tile_set'], [(228, 120, 8, 8)], C.BRICK_SIZE_MULTIPLIER)

class CastleFlag(Stuff):
    def __init__(self, x, y):
        Stuff.__init__(self, x, y, setup.GRAPHICS['item_objects'], [(129, 2, 14, 14)], C.SIZE_MULTIPLIER)
        self.target_height = y
        self.y_vel = -2

    def update(self):
        if self.rect.bottom > self.target_height:
            self.rect.y += self.y_vel


class Score(pygame.sprite.Sprite):
    def __init__(self, x, y, score):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.score = score
        self.y_vel = -3
        self.distance = 130 if self.score == 1000 else 75
        self.image = pygame.Surface((len(str(self.score)) * 10 * C.BRICK_SIZE_MULTIPLIER, 10 * C.BRICK_SIZE_MULTIPLIER)).convert()
        self.image.set_colorkey((0,0,0)) # 透明底
        self.rect = self.image.get_rect()
        self.create_score_image()

    def create_score_image(self):
        # 有些数字用不到，暂时没写坐标
        digit_rect_list = [(1, 168, 3, 8), (5, 168, 3, 8),
                            (8, 168, 4, 8), (0, 0, 0, 0),
                            (12, 168, 4, 8), (16, 168, 5, 8),
                            (0, 0, 0, 0), (0, 0, 0, 0),
                            (20, 168, 4, 8), (0, 0, 0, 0)]
        for i, digit in enumerate(str(self.score)):
            digit_rect = digit_rect_list[int(digit)]
            image = tools.get_image(setup.GRAPHICS['item_objects'], *digit_rect, (0,0,0), C.BRICK_SIZE_MULTIPLIER)
            self.image.blit(image, (i * 10, 0))
        self.rect.x = self.x
        self.rect.y = self.y - 10

    def update(self):
        self.rect.y += self.y_vel
        self.distance += self.y_vel
        if self.distance < 0:
            self.kill()


