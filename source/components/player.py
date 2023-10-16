import pygame
from .. import constants as C
from .. import setup
from .. import tools
from ..components import powerup
import json
import os


class Player(pygame.sprite.Sprite):
    def __init__(self, player_name):
        super(Player, self).__init__()
        self.player_name = player_name
        self.load_data()
        self.setup_timer()
        self.setup_state()
        self.setup_speed()
        self.load_images()

        self.frame_index = 0
        self.state = C.STAND
        self.image = self.right_frames[self.frame_index]
        self.rect = self.image.get_rect()

    def restart(self):
        if self.dead:
            self.dead = False
            self.big = False
            self.fire = False
            self.set_player_image(self.small_normal_frames, 0)
            self.right_frames = self.small_normal_frames[0]
            self.left_frames = self.small_normal_frames[1]
        self.state = C.STAND

    def load_data(self):
        player_file = self.player_name + '.json'
        file_path = os.path.join('source/data/player', player_file)
        with open(file_path) as f:
            self.player_data = json.load(f)

    def setup_timer(self):
        self.walking_timer = 0
        self.death_timer = 0
        self.flagpole_timer = 0
        self.transition_timer = 0
        self.hurt_invincible_timer = 0
        self.invincible_timer = 0
        self.last_fire_ball_timer = 0

    def load_images(self):
        sheet = setup.GRAPHICS['mario_bros']
        frames_list = self.player_data[C.PLAYER_FRAMES]

        self.right_small_normal_frames = []
        self.right_big_normal_frames = []
        self.right_big_fire_frames = []
        self.left_small_normal_frames = []
        self.left_big_normal_frames = []
        self.left_big_fire_frames = []

        self.small_normal_frames = [self.right_small_normal_frames, self.left_small_normal_frames]
        self.big_normal_frames = [self.right_big_normal_frames, self.left_big_normal_frames]
        self.big_fire_frames = [self.right_big_fire_frames, self.left_big_fire_frames]

        self.all_frames = [
            self.right_small_normal_frames,
            self.left_small_normal_frames,
            self.right_big_normal_frames,
            self.left_big_normal_frames,
            self.right_big_fire_frames,
            self.left_big_fire_frames
        ]


        self.right_frames = self.right_small_normal_frames
        self.left_frames = self.left_small_normal_frames

        for name, frames in frames_list.items():
            for frame in frames:
                image = tools.get_image(sheet, frame['x'], frame['y'], frame['width'], frame['height'], (0, 0, 0), C.SIZE_MULTIPLIER)
                left_image = pygame.transform.flip(image, True, False)
                if name == C.RIGHT_SMALL_NORMAL:
                    self.right_small_normal_frames.append(image)
                    self.left_small_normal_frames.append(left_image)
                if name == C.RIGHT_BIG_NORMAL:
                    self.right_big_normal_frames.append(image)
                    self.left_big_normal_frames.append(left_image)
                if name == C.RIGHT_BIG_FIRE:
                    self.right_big_fire_frames.append(image)
                    self.left_big_fire_frames.append(left_image)





    def set_player_image(self, frames, frame_index):
        self.frame_index = frame_index
        if self.facing_right:
            self.right_frames = frames[0]
            self.image = self.right_frames[frame_index]
        else:
            self.left_frames = frames[1]
            self.image = self.left_frames[frame_index]
        bottom = self.rect.bottom
        centerx = self.rect.centerx
        self.rect = self.image.get_rect()
        self.rect.bottom = bottom
        self.rect.centerx = centerx

    def setup_state(self):
        self.dead = False
        self.facing_right = True
        self.allow_jump = True
        self.allow_fireball = True
        self.big = False
        self.fire = False
        self.hurt_invincible = False
        self.invincible = False

    def setup_speed(self):
        speed = self.player_data[C.PLAYER_SPEED]
        self.x_vel = 0
        self.y_vel = 0

        self.max_walk_vel = speed[C.MAX_WALK_SPEED]
        self.max_run_vel = speed[C.MAX_RUN_SPEED]
        self.max_y_vel = speed[C.MAX_Y_VEL]
        self.walk_accel = speed[C.WALK_ACCEL]
        self.run_accel = speed[C.RUN_ACCEL]
        self.jump_vel = speed[C.JUMP_VEL]

        self.gravity = C.GRAVITY
        # 下面两个不知道干嘛的
        self.max_x_vel = self.max_walk_vel
        self.x_accel = self.walk_accel

    def update(self, keys, game_info, fire_group):
        self.current_time = game_info[C.CURRENT_TIME]
        self.handle_state(keys, fire_group)
        self.check_if_hurt_invincible()
        self.check_if_vincible()
        self.animate()

    def handle_state(self, keys, fire_group):
        if self.state == C.STAND:
            self.standing(keys, fire_group)
        elif self.state == C.WALK:
            self.walking(keys, fire_group)
        elif self.state == C.WALK_AUTO:
            self.walk_auto()
        elif self.state == C.JUMP:
            self.jumping(keys, fire_group)
        elif self.state == C.FALL:
            self.falling(keys, fire_group)
        elif self.state == C.DEATH_JUMP:
            self.jumping_to_death()
        elif self.state == C.SMALL_TO_BIG:
            self.y_vel = -1
            self.changing_to_big()
        elif self.state == C.BIG_TO_SMALL or self.state == C.FIRE_TO_SMALL:
            self.changing_to_small()
        elif self.state == C.BIG_TO_FIRE:
            self.changing_to_fire()
        elif self.state == C.FLAGPOLE:
            self.sliding_down_flag()
        elif self.state == C.IN_CASTLE:
            self.frame_index = 0
        elif self.state == C.CROUCH:
            self.crouching(keys)
        elif self.state == C.DOWN_TO_PIPE:
            self.y_vel = 1
            self.rect.y += self.y_vel # 因为down to pipe 在frozen state状态下，不会调用update player position
        elif self.state == C.UP_OUT_PIPE:
            self.y_vel = -1
            self.rect.y += self.y_vel
            if self.rect.bottom < self.up_pipe_y:
                self.rect.bottom = self.up_pipe_y
                self.state = C.STAND

    def standing(self, keys, fire_group):
        self.check_to_allow_jump(keys)
        self.check_to_allow_fireball(keys)

        self.frame_index = 0
        self.x_vel = 0
        self.y_vel = 0

        if keys[tools.keybinding['action']]:
            if self.fire and self.allow_fireball:
                self.shoot_fireball(fire_group)

        if keys[tools.keybinding['down']]:
            self.state = C.CROUCH

        if keys[tools.keybinding['left']]:
            self.facing_right = False
            self.state = C.WALK
        elif keys[tools.keybinding['right']]:
            self.facing_right = True
            self.state = C.WALK
        elif keys[tools.keybinding['jump']]:
            if self.allow_jump:
                if self.big:
                    setup.SOUNDS['big_jump'].play()
                else:
                    setup.SOUNDS['small_jump'].play()
                self.state = C.JUMP
                self.y_vel = self.jump_vel

    def crouching(self, keys):
        if keys[tools.keybinding['down']]:
            if self.big:
                self.frame_index = 7
                bottom = self.rect.bottom
                centerx = self.rect.centerx
                if self.facing_right:
                    self.image = self.right_frames[self.frame_index]
                else:
                    self.image = self.left_frames[self.frame_index]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
                self.rect.centerx = centerx
            if self.facing_right:
                if self.x_vel > 0:
                    self.x_vel -= self.x_accel
                else:
                    self.x_vel = 0
            else:
                if self.x_vel < 0:
                    self.x_vel += self.x_accel
                else:
                    self.x_vel = 0
        else:
            if self.big:
                self.frame_index = 0
                bottom = self.rect.bottom
                centerx = self.rect.centerx
                if self.facing_right:
                    self.image = self.right_frames[self.frame_index]
                else:
                    self.image = self.left_frames[self.frame_index]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
                self.rect.centerx = centerx
            if self.x_vel == 0:
                self.state = C.STAND
            else:
                self.state = C.WALK

    def walking(self, keys, fire_group):
        self.check_to_allow_jump(keys)
        self.check_to_allow_fireball(keys)

        if self.frame_index == 0:
            self.frame_index += 1
            self.walking_timer = self.current_time
        # 为了让高速状态下步频快一些
        elif (self.current_time - self.walking_timer) > self.calculate_animation_speed():
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 1
            self.walking_timer = self.current_time

        if keys[tools.keybinding['down']]:
            self.state = C.CROUCH

        if keys[tools.keybinding['action']]:
            self.max_x_vel = self.max_run_vel
            self.x_accel = self.run_accel
            if self.fire and self.allow_fireball:
                self.shoot_fireball(fire_group)
        else:
            self.max_x_vel = self.max_walk_vel
            self.x_accel = self.walk_accel

        # 处理持续按键持续跳的情况
        if keys[tools.keybinding['jump']]:
            if self.allow_jump:
                if self.big:
                    setup.SOUNDS['big_jump'].play()
                else:
                    setup.SOUNDS['small_jump'].play()
                self.state = C.JUMP
                if abs(self.x_vel) > 4:
                    self.y_vel = self.jump_vel - 0.5
                else:
                    self.y_vel = self.jump_vel

        if keys[tools.keybinding['left']]:
            self.facing_right = False
            if self.x_vel > 0:
                self.frame_index = 5
                self.x_accel = C.SMALL_TURNAROUND
            self.x_vel = self.calc_vel(self.x_vel, self.max_x_vel, self.x_accel, True)
        elif keys[tools.keybinding['right']]:
            self.facing_right = True
            if self.x_vel < 0:
                self.frame_index = 5
                self.x_accel = C.SMALL_TURNAROUND
            self.x_vel = self.calc_vel(self.x_vel, self.max_x_vel, self.x_accel, False)

        # 回归站立
        else:
            if self.facing_right:
                if self.x_vel > 0:
                    self.x_vel -= self.x_accel
                else:
                    self.x_vel = 0
                    self.state = C.STAND
            else:
                if self.x_vel < 0:
                    self.x_vel += self.x_accel
                else:
                    self.x_vel = 0
                    self.state = C.STAND

    def walk_auto(self):
        self.x_vel = 3 # HARD CODE HALF OF MAX SPEED
        self.y_vel = self.calc_vel(self.y_vel, self.max_y_vel, self.gravity)

        if self.current_time - self.walking_timer > 50:
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 1
            self.walking_timer = self.current_time


    def check_to_allow_jump(self, keys):
        if not keys[tools.keybinding['jump']]:
            self.allow_jump = True

    def jumping(self, keys, fire_group):
        self.check_to_allow_fireball(keys)
        self.allow_jump = False
        self.frame_index = 4
        self.gravity = C.JUMP_GRAVITY
        self.y_vel += self.gravity

        if self.y_vel >= 0 and self.y_vel < self.max_y_vel:
            self.gravity = C.GRAVITY
            self.state = C.FALL

        if keys[tools.keybinding['action']]:
            if self.fire and self.allow_fireball:
                self.shoot_fireball(fire_group)

        if keys[tools.keybinding['right']]:
            self.x_vel = self.calc_vel(self.x_vel, self.max_x_vel, self.x_accel)
        elif keys[tools.keybinding['left']]:
            self.x_vel = self.calc_vel(self.x_vel, self.max_x_vel, self.x_accel, isNeg=True)

        # 短跳
        if not keys[tools.keybinding['jump']]:
            self.gravity = C.GRAVITY
            self.state = C.FALL

    def falling(self, keys, fire_group):
        self.check_to_allow_fireball(keys)
        self.y_vel = self.calc_vel(self.y_vel, self.max_y_vel, self.gravity)

        if keys[tools.keybinding['action']]:
            if self.fire and self.allow_fireball:
                self.shoot_fireball(fire_group)

        if keys[tools.keybinding['right']]:
            self.x_vel = self.calc_vel(self.x_vel, self.max_x_vel, self.x_accel)
        elif keys[tools.keybinding['left']]:
            self.x_vel = self.calc_vel(self.x_vel, self.max_x_vel, self.x_accel, isNeg=True)


    def shoot_fireball(self, fire_group):
        if self.current_time - self.last_fire_ball_timer > 500:
            setup.SOUNDS['fireball'].play()
            self.allow_fireball = False #?
            fire_group.add(powerup.FireBall(self.rect.x, self.rect.y, self.facing_right))
            self.last_fire_ball_timer = self.current_time #?
            self.frame_index = 6

    def check_to_allow_fireball(self, keys):
        if not keys[tools.keybinding['action']]:
            self.allow_fireball = True

    def jumping_to_death(self):
        if self.death_timer == 0:
            self.death_timer = self.current_time
        elif self.current_time - self.death_timer > 500:
            self.rect.y += self.y_vel
            self.y_vel += self.gravity

    # 这个函数回头可以去掉isNeg
    def calc_vel(self, vel, max_vel, accel, isNeg=False):
        if isNeg:
            vel = vel * -1
        if vel + accel < max_vel:
            vel += accel
        else:
            vel = max_vel
        if isNeg:
            return vel * -1
        else:
            return vel

    def calculate_animation_speed(self):
        # 不知道为什么选13
        if self.x_vel == 0:
            animation_speed = 130
        elif self.x_vel > 0:
            animation_speed = 130 - self.x_vel * 13
        else:
            animation_speed = 130 + self.x_vel * 13
        return animation_speed

    def check_if_hurt_invincible(self):
        if self.hurt_invincible:
            if self.hurt_invincible_timer == 0:
                self.hurt_invincible_timer = self.current_time
                self.hurt_invincible_interval = self.current_time
            elif self.current_time - self.hurt_invincible_timer < 2000:
                if self.current_time - self.hurt_invincible_interval < 35:
                    self.image.set_alpha(0)
                elif self.current_time - self.hurt_invincible_interval < 70:
                    self.image.set_alpha(255)
                else:
                    self.hurt_invincible_interval = self.current_time
            else:
                self.hurt_invincible = False
                self.hurt_invincible_timer = 0
                for frames in self.all_frames:
                    for image in frames:
                        image.set_alpha(255)


    def check_if_vincible(self):
        if self.invincible:
            if self.invincible_timer == 0:
                self.invincible_timer = self.current_time
                self.invincible_interval = self.current_time
            elif self.current_time - self.invincible_timer < 10000:
                if self.current_time - self.invincible_interval < 35:
                    self.image.set_alpha(0)
                elif self.current_time - self.invincible_interval < 70:
                    self.image.set_alpha(255)
                else:
                    self.invincible_interval = self.current_time
            elif self.current_time - self.invincible_timer < 12000:
                if self.current_time - self.invincible_interval < 100:
                    self.image.set_alpha(0)
                elif self.current_time - self.invincible_interval < 200:
                    self.image.set_alpha(255)
                else:
                    self.invincible_interval = self.current_time
            else:
                self.invincible = False
                self.invincible_timer = 0
                for frames in self.all_frames:
                    for image in frames:
                        image.set_alpha(255)


    def animate(self):
        if self.facing_right:
            self.image = self.right_frames[self.frame_index]
        else:
            self.image = self.left_frames[self.frame_index]

    def start_death_jump(self):
        self.dead = True
        self.y_vel = -11
        self.gravity = .5
        self.frame_index = 6
        self.state = C.DEATH_JUMP
        self.invincible = False
        self.check_if_vincible() # 为了让透明的状态回来


    def changing_to_small(self):
        last_time = [265, 330, 395, 460, 525, 590, 655, 720, 785, 850, 915]
        size_list = [0, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2] # 0 big 1 medium 2 small
        frames = [(self.big_normal_frames, 4), (self.big_normal_frames, 8), (self.small_normal_frames, 8)]
        if self.transition_timer == 0:
            self.big = False
            self.fire = False
            self.hurt_invincible = True
            self.transition_timer = self.current_time
            self.change_index = 0
        elif self.current_time - self.transition_timer > last_time[self.change_index]:
            if self.change_index + 1 == len(size_list):
                self.transition_timer = 0
                self.set_player_image(self.small_normal_frames, 0)
                self.state = C.WALK
                self.right_frames = self.right_small_normal_frames
                self.left_frames = self.left_small_normal_frames
            else:
                frames, frame_index = frames[size_list[self.change_index]]
                self.set_player_image(frames, frame_index)
                self.change_index += 1


    def changing_to_big(self):
        last_time = [135, 200, 365, 430, 495, 560, 625, 690, 755, 820, 885]
        size_list = [1, 0, 1, 0, 1, 2, 0, 1, 2, 0, 2] # 0 small 1 medium 2 big
        frames = [(self.small_normal_frames, 0), (self.small_normal_frames, 7), (self.big_normal_frames, 0)]
        if self.transition_timer == 0:
            self.big = True
            self.transition_timer = self.current_time
            self.change_index = 0
        elif self.current_time - self.transition_timer > last_time[self.change_index]:
            if self.change_index + 1 == len(size_list):
                self.transition_timer = 0
                self.set_player_image(self.big_normal_frames, 0)
                self.state = C.WALK
                self.right_frames = self.right_big_normal_frames
                self.left_frames = self.left_big_normal_frames
            else:
                frames, frame_index = frames[size_list[self.change_index]]
                self.set_player_image(frames, frame_index)
                self.change_index += 1

    def changing_to_fire(self):
        last_time = [65, 195, 260, 325, 390, 455, 520, 585, 650, 715, 780, 845, 910, 975]
        size_list = [0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1]  # size value 0:fire, 1:big green, 2:big red, 3:big black
        frames = [(self.big_fire_frames, 3), (self.big_normal_frames, 3),
                  (self.big_fire_frames, 3), (self.big_normal_frames, 3)] # TODO 有重复有什么意义呢
        if self.transition_timer == 0:
            self.fire = True
            self.transition_timer = self.current_time
            self.change_index = 0
        elif self.current_time - self.transition_timer > last_time[self.change_index]:
            if self.change_index + 1 == len(size_list):
                self.transition_timer = 0
                self.set_player_image(self.big_fire_frames, 0)
                self.state = C.WALK
                self.right_frames = self.right_big_fire_frames
                self.left_frames = self.left_big_fire_frames
            else:
                frames, frame_index = frames[size_list[self.change_index]]
                self.set_player_image(frames, frame_index)
                self.change_index += 1

    def sliding_down_flag(self):
        self.x_vel = 0
        self.y_vel = 5

        if self.flagpole_timer == 0:
            self.flagpole_timer = self.current_time
        if self.rect.bottom < 493:
            if self.current_time - self.flagpole_timer < 65:
                self.frame_index = 9
            elif self.current_time - self.flagpole_timer < 130:
                self.frame_index = 10
            else:
                self.flagpole_timer = self.current_time
        else:
            self.frame_index = 10
