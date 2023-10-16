import pygame
from .. import setup, tools
from .. import constants as C

ENEMY_SPEED = 1


def create_enemy(item):
    dir = C.LEFT if item['direction'] == 0 else C.RIGHT
    color = item[C.COLOR]
    if C.ENEMY_RANGE in item:
        in_range = item[C.ENEMY_RANGE]
        range_start = item['range_start']
        range_end = item['range_end']
    else:
        in_range = False
        range_start = range_end = 0

    if item['type'] == C.ENEMY_TYPE_GOOMBA:
        sprite = Goomba(item['x'], item['y'], dir, color, in_range, range_start, range_end)
    elif item['type'] == C.ENEMY_TYPE_KOOPA:
        sprite = Koopa(item['x'], item['y'], dir, color, in_range, range_start, range_end)
    return sprite


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

    def setup_enemy(self, x, y, direction, name, sheet, frame_rect_list, in_range, range_start, range_end, isVertical=False):
        self.frames = []
        self.frame_index = 0
        self.animation_timer = 0
        self.gravity = 1.5
        self.state = C.WALK

        self.name = name
        self.direction = direction
        self.load_frames(sheet, frame_rect_list)
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y #? why bottom
        self.in_range = in_range
        self.range_start = range_start
        self.range_end = range_end
        self.isVertical = isVertical
        self.set_velocity()
        self.death_timer = 0

    def load_frames(self, sheet, frame_rect_list):
        for frame_rect in frame_rect_list:
            self.frames.append(tools.get_image(sheet, *frame_rect, (0, 0, 0), C.SIZE_MULTIPLIER))

    def set_velocity(self):
        if self.isVertical:
            self.x_vel = 0
            self.y_vel = ENEMY_SPEED
        else:
            self.x_vel = ENEMY_SPEED * -1 if self.direction == C.LEFT else ENEMY_SPEED
            self.y_vel = 0

    def update(self, game_info, level):
        self.current_time = game_info[C.CURRENT_TIME]
        self.handle_state()
        self.image = self.frames[self.frame_index]
        self.update_position(level)

    def handle_state(self):
        if self.state == C.WALK:
            self.walking()
        elif self.state == C.FALL:
            self.falling()
        elif self.state == C.DEATH_JUMP:
            self.death_jumping()
        elif self.state == C.JUMPED_ON:
            self.jumped_on()

    def walking(self):
        if self.current_time - self.animation_timer > 125:
            if self.direction == C.RIGHT:
                if self.frame_index == 4:
                    self.frame_index = 5
                else:
                    self.frame_index = 4
            else:
                if self.frame_index == 0:
                    self.frame_index = 1
                else:
                    self.frame_index = 0
            self.animation_timer = self.current_time

    def falling(self):
        if self.y_vel < 10:
            self.y_vel += self.gravity

    def death_jumping(self):
        self.rect.y += self.y_vel
        self.rect.x += self.x_vel
        self.y_vel += self.gravity
        if self.rect.y > C.SCREEN_H:
            self.kill()

    def jumped_on(self):
        pass

    def start_death_jump(self, direction):
        self.y_vel = -8
        self.x_vel = 2 if direction == C.RIGHT else -2
        self.gravity = .5
        self.frame_index = 3
        self.state = C.DEATH_JUMP

    def update_position(self, level):
        self.rect.x += self.x_vel
        self.check_x_collisions(level)

        if self.in_range and self.isVertical:
            if self.rect.y < self.range_start:
                self.rect.y = self.range_start
                self.y_vel = ENEMY_SPEED
            elif self.rect.y > self.range_end:
                self.rect.y = self.range_end
                self.y_vel = -1 * ENEMY_SPEED
        self.rect.y += self.y_vel

        if self.state != C.DEATH_JUMP:
            self.check_y_collisions(level)

        if self.rect.x <= 0 or self.rect.y > C.SCREEN_H:
            self.kill()

    def check_x_collisions(self, level):
        if self.in_range and not self.isVertical:
            if self.rect.x < self.range_start:
                self.rect.x = self.range_start
                self.change_direction(C.RIGHT)
            elif self.rect.x > self.range_end:
                self.rect.right = self.range_end
                self.change_direction(C.LEFT)
        else:
            sprite = pygame.sprite.spritecollideany(self, level.ground_step_pipe_group)
            if sprite:
                if self.direction == C.LEFT:
                    self.rect.left = sprite.rect.right
                    self.change_direction(C.RIGHT)
                elif self.direction == C.RIGHT:
                    self.rect.right = sprite.rect.left
                    self.change_direction(C.LEFT)

        if self.state == C.SHELL_SLIDE:
            enemy = pygame.sprite.spritecollideany(self, level.enemy_group)
            if enemy:
                level.enemy_group.remove(enemy)
                level.dying_group.add(enemy)
                enemy.start_death_jump(self.direction)

    def change_direction(self, direction):
        self.direction = direction
        self.x_vel *= -1
        if self.direction == C.RIGHT:
            if self.state == C.WALK:
                self.frame_index = 4
        elif self.direction == C.LEFT:
            if self.state == C.WALK:
                self.frame_index = 0


    def check_y_collisions(self, level):
        sprite_group = pygame.sprite.Group(level.ground_step_pipe_group, level.brick_group, level.box_group)
        sprite = pygame.sprite.spritecollideany(self, sprite_group)
        if sprite:
            if self.rect.top <= sprite.rect.top: # 敌人只会往下走 不会往上跳？
                self.rect.bottom = sprite.rect.y
                self.y_vel = 0
                self.state = C.WALK
        level.check_is_falling(self) # 卧槽，反向调用


class Goomba(Enemy):
    def __init__(self, x, y, direction, color, in_range, range_start, range_end, name=C.GOOMBA):
        Enemy.__init__(self)
        frame_rect_list = self.get_frame_rect(color)
        self.setup_enemy(x, y, direction, name, setup.GRAPHICS['smb_enemies_sheet'], frame_rect_list, in_range, range_start, range_end)
        self.frames.append(pygame.transform.flip(self.frames[2], False, True))
        self.frames.append(pygame.transform.flip(self.frames[0], True, False))
        self.frames.append(pygame.transform.flip(self.frames[1], True, False))

    def get_frame_rect(self, color):
        if color == C.COLOR_TYPE_GREEN:
            frame_rect_list = [(0, 34, 16, 16), (30, 34, 16, 16),
                        (61, 30, 16, 16)]
        else:
            frame_rect_list = [(0, 4, 16, 16), (30, 4, 16, 16),
                        (61, 0, 16, 16)]
        return frame_rect_list

    def jumped_on(self):
        self.x_vel = 0
        self.frame_index = 2
        if self.death_timer == 0:
            self.death_timer = self.current_time
        elif self.current_time - self.death_timer > 500:
            self.kill()


class Koopa(Enemy):
    def __init__(self, x, y, direction, color, in_range, range_start, range_end, name=C.KOOPA):
        Enemy.__init__(self)
        frame_rect_list = self.get_frame_rect(color)
        self.setup_enemy(x, y, direction, name, setup.GRAPHICS['smb_enemies_sheet'], frame_rect_list, in_range,
                         range_start, range_end)
        self.frames.append(pygame.transform.flip(self.frames[2], False, True))
        self.frames.append(pygame.transform.flip(self.frames[0], True, False))
        self.frames.append(pygame.transform.flip(self.frames[1], True, False))

    def get_frame_rect(self, color):
        if color == C.COLOR_TYPE_GREEN:
            frame_rect_list = [(150, 0, 16, 24), (180, 0, 16, 24),
                               (360, 5, 16, 15)]
        elif color == C.COLOR_TYPE_RED:
            frame_rect_list = [(150, 30, 16, 24), (180, 30, 16, 24),
                               (360, 35, 16, 15)]
        else:
            frame_rect_list = [(150, 60, 16, 24), (180, 60, 16, 24),
                               (360, 65, 16, 15)]
        return frame_rect_list

    def jumped_on(self):
        self.x_vel = 0
        self.frame_index = 2
        bottom = self.rect.bottom
        x = self.rect.x
        self.rect = self.frames[self.frame_index].get_rect()
        self.rect.bottom = bottom
        self.rect.x = x
        self.in_range = False