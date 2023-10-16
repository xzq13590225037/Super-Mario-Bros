import pygame
from .. import setup, tools
from .. import constants as C


def create_powerup(centerx, y, type, game_info):
    if type in [C.TYPE_MUSHROOM, C.TYPE_FIREFLOWER]:
        if game_info[C.POWERUP_LEVEL] == C.SMALL:
            return Mushroom(centerx, y)
        else:
            return FireFlower(centerx, y)
    elif type == C.TYPE_STAR:
        return Star(centerx, y)
    elif type == C.TYPE_LIFEMUSHROOM:
        return LifeMushroom(centerx, y)


class Powerup(pygame.sprite.Sprite):
    def __init__(self, centerx, y, sheet, image_rect_list, scale):
        pygame.sprite.Sprite.__init__(self)

        self.frames = []
        self.frame_index = 0
        for image_rect in image_rect_list:
            self.frames.append(tools.get_image(sheet, *image_rect, (0,0,0), scale))
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.centerx = centerx
        self.rect.y = y
        self.state = C.REVEAL
        self.x_vel = 0
        self.y_vel = -1
        self.direction = C.RIGHT
        self.box_height = y
        self.gravity = 1
        self.max_y_vel = 8
        self.speed = 0
        self.animation_timer = 0

    def update_position(self, level):
        self.rect.x += self.x_vel
        self.check_for_x_collision(level)
        self.rect.y += self.y_vel
        self.check_for_y_collision(level)

        if self.rect.x < 0:
            self.kill()
        elif self.rect.y > level.viewport.bottom:
            self.kill()

    def check_for_x_collision(self, level):
        sprite_group = pygame.sprite.Group(level.ground_step_pipe_group, level.brick_group, level.box_group)
        sprite = pygame.sprite.spritecollideany(self, sprite_group)

        if sprite:
            if self.direction == C.RIGHT:
                self.rect.right = sprite.rect.left
                self.direction = C.LEFT
            elif self.direction == C.LEFT:
                self.rect.left = sprite.rect.right
                self.direction = C.RIGHT
            self.x_vel = self.speed if self.direction == C.RIGHT else -1 * self.speed

    def check_for_y_collision(self, level):
        sprite_group = pygame.sprite.Group(level.ground_step_pipe_group, level.brick_group, level.box_group)
        sprite = pygame.sprite.spritecollideany(self, sprite_group)
        if sprite:
            self.y_vel = 0
            self.rect.bottom = sprite.rect.top
            self.state = C.SLIDE
        level.check_is_falling(self)

    def animation(self):
        self.image = self.frames[self.frame_index]


class Mushroom(Powerup):
    def __init__(self, centerx, y):
        Powerup.__init__(self, centerx, y, setup.GRAPHICS['item_objects'], [(0, 0, 16, 16)], C.SIZE_MULTIPLIER)
        self.type = C.TYPE_MUSHROOM
        self.speed = 2

    def update(self, game_info, level):
        if self.state == C.REVEAL:
            self.rect.y += self.y_vel
            if self.rect.bottom < self.box_height:
                self.rect.bottom = self.box_height
                self.y_vel = 0
                self.state = C.SLIDE
        elif self.state == C.SLIDE:
            self.x_vel = self.speed if self.direction == C.RIGHT else -1 * self.speed
        elif self.state == C.FALL:
            if self.y_vel < self.max_y_vel:
                self.y_vel += self.gravity

        if self.state == C.SLIDE or self.state == C.FALL:
            self.update_position(level)

        self.animation()


class FireFlower(Powerup):
    def __init__(self, centerx, y):
        frame_rect_list = [(0, 32, 16, 16), (16, 32, 16, 16),
                        (32, 32, 16, 16), (48, 32, 16, 16)]
        Powerup.__init__(self, centerx, y, setup.GRAPHICS['item_objects'], frame_rect_list, C.SIZE_MULTIPLIER)
        self.type = C.TYPE_FIREFLOWER

    def update(self, game_info, level):
        self.current_time = game_info[C.CURRENT_TIME]
        if self.state == C.REVEAL:
            self.rect.y += self.y_vel
            if self.rect.bottom < self.box_height:
                self.rect.bottom = self.box_height
                self.y_vel = 0
                self.state = C.RESTING
        if self.current_time - self.animation_timer > 30:
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 0
            self.animation_timer = self.current_time

        self.animation()


class Star(Powerup):
    def __init__(self, centerx, y):
        frame_rect_list = [(1, 48, 15, 16), (17, 48, 15, 16),
                        (33, 48, 15, 16), (49, 48, 15, 16)]
        Powerup.__init__(self, centerx, y, setup.GRAPHICS['item_objects'], frame_rect_list, C.SIZE_MULTIPLIER)
        self.type = C.TYPE_STAR

        self.gravity = 0.4
        self.speed = 5

    def update(self, game_info, level):
        self.current_time = game_info[C.CURRENT_TIME]
        if self.state == C.REVEAL:
            self.rect.y += self.y_vel
            if self.rect.bottom < self.box_height:
                self.rect.bottom = self.box_height
                self.y_vel = -2
                self.state = C.BOUNCING
        elif self.state == C.BOUNCING:
            self.y_vel += self.gravity
            self.x_vel = self.speed if self.direction == C.RIGHT else -self.speed
            self.update_position(level)

        if self.current_time - self.animation_timer > 30:
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 0
            self.animation_timer = self.current_time

        self.animation()

    def check_for_y_collision(self, level):
        sprite_group = pygame.sprite.Group(level.ground_step_pipe_group, level.box_group, level.brick_group)
        sprite = pygame.sprite.spritecollideany(self, sprite_group)

        if sprite:
            if self.rect.top > sprite.rect.top:
                self.rect.top = sprite.rect.bottom
                self.y_vel = 5
            else:
                self.y_vel = -5
                self.rect.bottom = sprite.rect.top


class LifeMushroom(Mushroom):
    def __init__(self, centerx, y):
        Powerup.__init__(self, centerx, y, setup.GRAPHICS['item_objects'], [(16, 0, 16, 16)], C.SIZE_MULTIPLIER)
        self.type = C.TYPE_LIFEMUSHROOM
        self.speed = 2


class FireBall(Powerup):
    def __init__(self, x, y, facing_right):
        # first 3 Frames are flying, last 4 frams are exploding
        frame_rect_list = [(96, 144, 8, 8), (104, 144, 8, 8),
                        (96, 152, 8, 8), (104, 152, 8, 8),
                        (112, 144, 16, 16), (112, 160, 16, 16),
                        (112, 176, 16, 16)]
        Powerup.__init__(self, x, y, setup.GRAPHICS['item_objects'], frame_rect_list, C.SIZE_MULTIPLIER)
        self.type = C.TYPE_FIREBALL
        self.y_vel = 10
        self.gravity = 0.9
        self.state = C.FLYING
        if facing_right:
            self.direction = C.RIGHT
            self.x_vel = 12
        else:
            self.direction = C.LEFT
            self.x_vel = -12

    def update(self, game_info, level):
        self.current_time = game_info[C.CURRENT_TIME]

        if self.state == C.FLYING or self.state == C.BOUNCING:
            self.y_vel += self.gravity
            if self.current_time - self.animation_timer > 200:
                if self.frame_index < 3:
                    self.frame_index += 1
                else:
                    self.frame_index = 0
                self.animation_timer = self.current_time
            self.update_position(level)
        elif self.state == C.EXPLODING:
            if self.current_time - self.animation_timer > 50:
                if self.frame_index < 6:
                    self.frame_index += 1
                else:
                    self.kill()
                self.animation_timer = self.current_time

        self.animation()

    def check_for_x_collision(self, level):
        sprite_group = pygame.sprite.Group(level.ground_step_pipe_group, level.brick_group, level.box_group)
        sprite = pygame.sprite.spritecollideany(self, sprite_group)
        if sprite:
            self.change_to_explode()

    def check_for_y_collision(self, level):
        sprite_group = pygame.sprite.Group(level.ground_step_pipe_group, level.brick_group, level.box_group)
        sprite = pygame.sprite.spritecollideany(self, sprite_group)
        enemy = pygame.sprite.spritecollideany(self, level.enemy_group)
        # 只处理落地后反弹，不处理碰上壁反弹
        if sprite:
            if self.rect.top > sprite.rect.top:
                self.change_to_explode()
            else:
                self.rect.bottom = sprite.rect.top
                self.y_vel = -8
            self.state = C.BOUNCING
        elif enemy:
            setup.SOUNDS['kick'].play()
            level.update_score(100, enemy)
            level.enemy_group.remove(enemy)
            level.dying_group.add(enemy)
            enemy.start_death_jump(self.direction)
            self.change_to_explode()

    def change_to_explode(self):
        self.frame_index = 4
        self.state = C.EXPLODING


