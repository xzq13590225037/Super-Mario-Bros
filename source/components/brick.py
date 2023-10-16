from .. import constants as C
from .stuff import Stuff
from .. import setup, tools
from .coin import Coin
from .powerup import create_powerup


class Brick(Stuff):
    def __init__(self, data, group=None, name=C.MAP_BRICK):
        x = data['x']
        y = data['y']
        type = data['type']
        color = data.get('color', C.COLOR_TYPE_ORANGE)
        orange_rect = [(16, 0, 16, 16), (432, 0, 16, 16)]
        green_rect = [(208, 32, 16, 16), (48, 32, 16, 16)]

        if color == C.COLOR_TYPE_ORANGE:
            frame_rect = orange_rect
        else:
            frame_rect = green_rect
        Stuff.__init__(self, x, y, setup.GRAPHICS['tile_set'], frame_rect, C.BRICK_SIZE_MULTIPLIER)
        self.rest_height = y
        self.state = C.RESTING
        self.y_vel = 0
        self.gravity = 1.2
        self.type = type
        if self.type == C.TYPE_COIN:
            self.coin_num = 10
        else:
            self.coin_num = 0
        self.group = group
        self.name = name

    def update(self, game_info):
        if self.state == C.BUMPED:
            self.bumped(game_info)

        if self.state == C.OPENED:
            self.opened()

    def opened(self):
        self.frame_index = 1
        self.image = self.frames[self.frame_index]

    def bumped(self, game_info):
        self.rect.y += self.y_vel
        self.y_vel += self.gravity

        if self.rect.y >= self.rest_height:
            self.rect.y = self.rest_height

            if self.type == C.TYPE_COIN:
                if self.coin_num > 0:
                    setup.SOUNDS['coin'].play()
                    self.group.add(Coin(self.rect.centerx, self.rect.y))
                    self.coin_num -= 1
                    self.state = C.RESTING
                else:
                    self.state = C.OPENED
            elif self.type in [C.TYPE_MUSHROOM, C.TYPE_FIREFLOWER, C.TYPE_LIFEMUSHROOM, C.TYPE_STAR]:
                setup.SOUNDS['powerup_appears'].play()
                self.group.add(create_powerup(self.rect.centerx, self.rect.y, self.type, game_info))
                self.state = C.OPENED
            else:
                self.state = C.RESTING

    def start_bump(self):
        self.y_vel = -7
        self.state = C.BUMPED

    def change_to_pieces(self, group):
        pieces = [(self.rect.x, self.rect.y - self.rect.height/2, -2, -12),
                    (self.rect.x, self.rect.y, -2, -6),
                    (self.rect.right, self.rect.y - self.rect.height/2, 2, -12),
                    (self.rect.right, self.rect.y, 2, -6),]

        for piece in pieces:
            group.add(BrickPiece(*piece))
        self.kill()


class BrickPiece(Stuff):
    def __init__(self, x, y, x_vel, y_vel):
        Stuff.__init__(self, x, y, setup.GRAPHICS['tile_set'], [(68, 20, 8, 8)], C.BRICK_SIZE_MULTIPLIER)
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.gravity = 0.8

    def update(self, *args):
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel
        self.y_vel += self.gravity
        if self.rect.y > C.SCREEN_H:
            self.kill()




