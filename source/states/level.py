from .. import tools
from .. import setup
from .. import constants as C
from ..components import info
import os
import json
import pygame
from ..components import player, stuff, coin, brick, box, enemy
from ..sound import Sound


class Level(tools.State):
    def __init__(self):
        super(Level, self).__init__()
        self.player = None

    def startup(self, current_time, game_info):
        self.game_info = game_info
        self.game_info[C.CURRENT_TIME] = current_time
        self.death_timer = 0
        self.castle_timer = 0
        self.score_group = pygame.sprite.Group()
        self.overhead_info = info.Info(self.game_info, C.LEVEL)
        self.sound = Sound(C.LEVEL)
        self.load_map() # 导入某一关的地图JSON文件
        self.setup_background() # 读取具体的图片数据
        self.setup_maps() # 设置地图起始位置，玩家起始位置
        self.ground_group = self.setup_collide(C.MAP_GROUND) # 地面
        self.step_group = self.setup_collide(C.MAP_STEP) # 台阶:
        self.pipe_group = self.setup_collide(C.MAP_PIPE) # 管子
        self.setup_pipe() # 暂时注释掉，以后更改为管子的某一个部分可以进入
        self.setup_static_coin()
        self.setup_brick_and_box() # 设置各个砖块及蘑菇
        self.setup_player()
        self.setup_enemies()
        self.setup_checkpoints()
        self.setup_flagpole()
        self.setup_sprite_groups()

    def load_map(self):
        map_file = 'level_' + str(self.game_info[C.LEVEL_NUM]) + '.json'
        file_path = os.path.join('source/data/maps', map_file)
        with open(file_path) as f:
            self.map_data = json.load(f)

    def setup_background(self):
        img_name = self.map_data[C.MAP_IMAGE]
        self.background = setup.GRAPHICS[img_name]
        self.bg_rect = self.background.get_rect()
        self.background = pygame.transform.scale(self.background,
                                                 (int(self.bg_rect.width * C.BACKGROUND_MULTIPLIER),
                                                  int(self.bg_rect.height * C.BACKGROUND_MULTIPLIER),))
        self.bg_rect = self.background.get_rect()
        self.level = pygame.Surface((self.bg_rect.w, self.bg_rect.h)).convert() # 不知道创建这个surface干嘛用
        self.viewport = setup.SCREEN.get_rect(bottom=self.bg_rect.bottom)

    def setup_maps(self):
        self.map_list = []
        if C.MAP_MAPS in self.map_data:
            for data in self.map_data[C.MAP_MAPS]:
                self.map_list.append((data['start_x'], data['end_x'], data['player_x'], data['player_y']))
            self.start_x, self.end_x, self.player_x, self.player_y = self.map_list[0]
        else:
            self.start_x, self.end_x, self.player_x, self.player_y = 0, self.bg_rect.w, 110, C.GROUND_HEIGHT

    def setup_collide(self, name):
        group = pygame.sprite.Group()
        if name in self.map_data:
            for data in self.map_data[name]:
                group.add(stuff.Collider(data['x'], data['y'], data['width'], data['height'], name))
        return group

    def change_map(self, index, type):
        self.start_x, self.end_x, self.player_x, self.player_y = self.map_list[index]
        self.viewport.x = self.start_x
        if type == C.CHECKPOINT_TYPE_MAP:
            self.player.rect.x = self.viewport.x + self.player_x
            self.player.rect.y = self.viewport.y + self.player_y
            self.player.state = C.STAND
        elif type == C.CHECKPOINT_TYPE_PIPE_UP:
            self.player.rect.x = self.viewport.x + self.player_x
            self.player.rect.bottom = C.GROUND_HEIGHT
            self.player.state = C.UP_OUT_PIPE
            self.player.up_pipe_y = self.player_y # 最终到地面上的y

    def setup_pipe(self):
        self.pipe_group = pygame.sprite.Group()
        if C.MAP_PIPE in self.map_data:
            for data in self.map_data[C.MAP_PIPE]:
                self.pipe_group.add(stuff.Pipe(data['x'], data['y'], data['width'], data['height'], data['type'], name=C.MAP_PIPE))

    def setup_static_coin(self):
        self.static_coin_group = pygame.sprite.Group()
        if C.MAP_COIN in self.map_data:
            for data in self.map_data[C.MAP_COIN]:
                self.static_coin_group.add(coin.StaticCoin(data['x'], data['y']))

    def setup_brick_and_box(self):
        self.coin_group = pygame.sprite.Group()
        self.powerup_group = pygame.sprite.Group()
        self.brick_group = pygame.sprite.Group()
        self.box_group = pygame.sprite.Group()

        if C.MAP_BRICK in self.map_data:
            for data in self.map_data[C.MAP_BRICK]:
                if data['type'] == C.TYPE_COIN:
                    self.brick_group.add(brick.Brick(data, group=self.coin_group))
                elif data['type'] in (C.TYPE_STAR, C.TYPE_FIREFLOWER, C.TYPE_MUSHROOM, C.TYPE_LIFEMUSHROOM):
                    self.brick_group.add(brick.Brick(data, group=self.powerup_group))
                else:
                    if C.BRICK_NUM in data:
                        direction = data[C.DIRECTION]
                        x = data['x']
                        y = data['y']
                        for i in range(data[C.BRICK_NUM]):
                            if direction == C.VERTICAL:
                                data['y'] = y + i * 43 # because 16*16 * multiplier  = 43
                                self.brick_group.add(brick.Brick(data))
                            else:
                                data['x'] = x + i * 43  # because 16*16 * multiplier  = 43
                                self.brick_group.add(brick.Brick(data))
                    else:
                        self.brick_group.add(brick.Brick(data))

        if C.MAP_BOX in self.map_data:
            for data in self.map_data[C.MAP_BOX]:
                if data['type'] == C.TYPE_COIN:
                    self.box_group.add(box.Box(data, group=self.coin_group))
                else:
                    self.box_group.add(box.Box(data, group=self.powerup_group))

    def setup_player(self):
        if self.player is None:
            self.player = player.Player(self.game_info[C.PLAYER_NAME])
        else:
            self.player.restart()
        self.player.rect.x = self.viewport.x + self.player_x
        self.player.rect.bottom = self.player_y
        # 不知道下面这句干嘛的 110和setup方法里玩家的初始位置110一致
        self.viewport.x = self.player.rect.x - 110

    def setup_enemies(self):
        self.enemy_group_list = []
        index = 0
        for data in self.map_data[C.MAP_ENEMY]:
            group = pygame.sprite.Group()
            for item in data[str(index)]:
                group.add(enemy.create_enemy(item))
            self.enemy_group_list.append(group)
            index += 1

    def setup_checkpoints(self):
        self.checkpoint_group = pygame.sprite.Group()
        for data in self.map_data[C.MAP_CHECKPOINT]:
            if C.ENEMY_GROUPID in data:
                enemy_groupid = data[C.ENEMY_GROUPID]
            else:
                enemy_groupid = 0 # 不知道为什么还能等于0，没有敌人的区域就没敌人呗?
            if C.MAP_INDEX in data:
                map_index = data[C.MAP_INDEX]
            else:
                map_index = 0
            self.checkpoint_group.add(stuff.Checkpoint(data['x'], data['y'], data['width'], data['height'],
                                                       data['type'], enemy_groupid, map_index))

    def setup_flagpole(self):
        self.flagpole_group = pygame.sprite.Group()
        if C.MAP_FLAGPOLE in self.map_data:
            for data in self.map_data[C.MAP_FLAGPOLE]:
                if data['type'] == C.FLAGPOLE_TYPE_FLAG:
                    sprite = stuff.Flag(data['x'], data['y'])
                    self.flag = sprite
                elif data['type'] == C.FLAGPOLE_TYPE_POLE:
                    sprite = stuff.Pole(data['x'], data['y'])
                elif data['type'] == C.FLAGPOLE_TYPE_TOP:
                    sprite = stuff.PoleTop(data['x'], data['y'])
                self.flagpole_group.add(sprite)

    def setup_sprite_groups(self):
        self.enemy_group = pygame.sprite.Group() # 新建一个空列表，以防止enemy_group.update挂掉
        self.dying_group = pygame.sprite.Group()
        self.shell_group = pygame.sprite.Group()

        self.player_group = pygame.sprite.Group(self.player)
        # 一系列的地面物件
        self.ground_step_pipe_group = pygame.sprite.Group(self.ground_group, self.step_group, self.pipe_group) # 暂时只加了两个，管子滑块没加

    def update(self, surface, keys, current_time):
        self.game_info[C.CURRENT_TIME] = self.current_time = current_time
        self.handle_states(keys)
        self.draw(surface)

    def handle_states(self, keys):
        self.update_all_sprites(keys)

    def update_all_sprites(self, keys):
        if self.player.dead:
            self.player.update(keys, self.game_info, self.powerup_group)
            if self.current_time - self.death_timer > 3000:
                self.update_game_info()
                self.finished = True
        elif self.player.state == C.IN_CASTLE:
            self.player.update(keys, self.game_info, None)
            self.flagpole_group.update()
            if self.current_time - self.castle_timer > 5000:
                self.update_game_info()
                self.finished = True
        elif self.in_frozen_state():
            self.player.update(keys, self.game_info, None)
            self.check_checkpoints()
            self.update_viewport()
        else:
            self.player.update(keys, self.game_info, self.powerup_group)
            self.flagpole_group.update()
            self.check_checkpoints()
            self.static_coin_group.update(self.game_info)
            self.brick_group.update(self.game_info)
            self.box_group.update(self.game_info)
            self.coin_group.update(self.game_info)
            self.powerup_group.update(self.game_info, self)
            self.enemy_group.update(self.game_info, self)
            self.shell_group.update(self.game_info, self)
            self.update_player_position()
            self.dying_group.update(self.game_info, self)  #? why 要传入self
            self.check_for_player_death()
            self.update_viewport()
            self.score_group.update()
            self.overhead_info.update(self.game_info)
        self.sound.update(self.player, self.overhead_info.time)

    def check_checkpoints(self):
        checkpoint = pygame.sprite.spritecollideany(self.player, self.checkpoint_group)

        if checkpoint:
            if checkpoint.type == C.CHECKPOINT_TYPE_ENEMY:
                group = self.enemy_group_list[checkpoint.enemy_groupid]
                self.enemy_group.add(group)
            elif checkpoint.type == C.CHECKPOINT_TYPE_FLAG:
                self.player.state = C.FLAGPOLE
                print(self.player.rect.bottom, self.flag.rect.y)
                if self.player.rect.bottom < self.flag.rect.y:
                    self.player.rect.bottom = self.flag.rect.y
                self.flag.state = C.SLIDE_DOWN
                self.update_flag_score()
            elif checkpoint.type == C.CHECKPOINT_TYPE_MUSHROOM and self.player.y_vel < 0:
                data = {'x': checkpoint.rect.x, 'y':checkpoint.rect.bottom - 40, 'type': C.TYPE_LIFEMUSHROOM}
                mushroom_box = box.Box(data, group=self.powerup_group)
                self.box_group.add(mushroom_box)
                mushroom_box.start_bump()
                self.player.y_vel = 7
                self.player.rect.top = mushroom_box.rect.bottom
                self.player.state = C.FALL
            elif checkpoint.type == C.CHECKPOINT_TYPE_CASTLE:
                self.player.state = C.IN_CASTLE
                self.player.x_vel = 0
                self.player.y_vel = 0 # 必须写这个，不然就会触发撞地，然后改变状态了
                self.castle_timer = self.current_time
                self.flagpole_group.add(stuff.CastleFlag(8745, 322)) # hardcode???
            elif checkpoint.type == C.CHECKPOINT_TYPE_PIPE:
                self.player.state = C.WALK_AUTO
            elif checkpoint.type == C.CHECKPOINT_TYPE_MAP:
                self.change_map(checkpoint.map_index, checkpoint.type)
            elif checkpoint.type == C.CHECKPOINT_TYPE_PIPE_UP:
                self.change_map(checkpoint.map_index, checkpoint.type)
            checkpoint.kill()

    def update_flag_score(self):
        base_y = C.GROUND_HEIGHT - 80
        heights = [base_y, base_y - 120, base_y - 200, base_y - 320, 0]
        scores = [100, 400, 800, 2000, 5000]
        for height, score in zip(heights, scores):
            if height < self.player.rect.y:
                self.update_score(score, self.flag, 0)
                break

    def update_game_info(self):
        if self.player.dead:
            self.game_info[C.LIVES] -= 1
            self.game_info[C.POWERUP_LEVEL] = C.SMALL
        if self.game_info[C.LIVES] == 0:
            self.next = C.GAME_OVER
        elif self.overhead_info.time == 0:
            self.next = C.TIME_OUT
        elif self.player.dead:
            self.next = C.LOAD_SCREEN
        else:
            # self.game_info[C.LEVEL_NUM] += 1
            # self.next = C.LOAD_SCREEN
            self.next = C.GAME_OVER

    def update_player_position(self):
        # TODO 不是一个好办法
        if self.player.state == C.UP_OUT_PIPE:
            return

        self.player.rect.x += round(self.player.x_vel)
        if self.player.rect.x < self.start_x:
            self.player.rect.x = self.start_x
        elif self.player.rect.right > self.end_x:
            self.player.rect.right = self.end_x
        self.check_player_x_collisions()

        # 如果死了的话可以跌到谷底，否则碰到地面就复原
        if not self.player.dead:
            self.player.rect.y += round(self.player.y_vel)
            self.check_player_y_collisions()

    def check_player_x_collisions(self):
        ground_step_pipe = pygame.sprite.spritecollideany(self.player, self.ground_step_pipe_group)
        enemy = pygame.sprite.spritecollideany(self.player, self.enemy_group)
        brick = pygame.sprite.spritecollideany(self.player, self.brick_group)
        box = pygame.sprite.spritecollideany(self.player, self.box_group)
        powerup = pygame.sprite.spritecollideany(self.player, self.powerup_group)
        coin = pygame.sprite.spritecollideany(self.player, self.static_coin_group)
        shell = pygame.sprite.spritecollideany(self.player, self.shell_group)

        if brick:
            self.adjust_player_for_x_collisions(brick)
        elif box:
            self.adjust_player_for_x_collisions(box)
        elif ground_step_pipe:
            if ground_step_pipe.name == C.MAP_PIPE and ground_step_pipe.type == C.PIPE_TYPE_HORIZONTAL:
                return
            self.adjust_player_for_x_collisions(ground_step_pipe)
        elif enemy:
            if self.player.hurt_invincible:
                pass
            elif self.player.invincible:
                setup.SOUNDS['kick'].play()
                self.update_score(100, enemy, 0)
                self.enemy_group.remove(enemy)
                self.dying_group.add(enemy)
                direction = C.RIGHT if self.player.facing_right else C.LEFT
                enemy.start_death_jump(direction)
            elif self.player.big:
                setup.SOUNDS['pipe'].play()
                self.player.y_vel = -1 #?
                self.player.state = C.BIG_TO_SMALL
                self.game_info[C.POWERUP_LEVEL] = C.SMALL
            else:
                self.player.start_death_jump()
                self.death_timer = self.current_time
        elif powerup:
            if powerup.type == C.TYPE_MUSHROOM:
                setup.SOUNDS['powerup'].play()
                self.player.state = C.SMALL_TO_BIG
                self.game_info[C.POWERUP_LEVEL] = C.BIG
            elif powerup.type == C.TYPE_FIREFLOWER:
                setup.SOUNDS['powerup'].play()
                if not self.player.big:
                    self.player.state = C.SMALL_TO_BIG
                elif not self.player.fire:
                    self.player.state = C.BIG_TO_FIRE
                    self.game_info[C.POWERUP_LEVEL] = C.FIRE # TODO 可以直接用 PLAYER的.fire .big 不需要powerup level
            elif powerup.type == C.TYPE_STAR:
                self.player.invincible = True
            elif powerup.type == C.TYPE_LIFEMUSHROOM:
                setup.SOUNDS['one_up'].play()
                self.game_info[C.LIVES] += 1
            if powerup.type != C.TYPE_FIREBALL:
                self.update_score(1000, powerup, 0)
                powerup.kill() # TODO 如果是火球不会因碰撞消失
        elif shell:
            if shell.state == C.SHELL_SLIDE:
                if self.player.hurt_invincible:
                    pass
                elif self.player.invincible:
                    setup.SOUNDS['kick'].play()
                    self.update_score(200, shell, 0)
                    self.shell_group.remove(shell)
                    self.dying_group.add(shell)
                    direction = C.RIGHT if self.player.facing_right else C.LEFT
                    enemy.start_death_jump(direction)
                elif self.player.big:
                    self.player.y_vel = -1 #?
                    self.player.state = C.BIG_TO_SMALL
                    setup.SOUNDS['pipe'].play()
                else:
                    self.player.start_death_jump()
                    self.death_timer = self.current_time
            else:
                setup.SOUNDS['kick'].play()
                self.update_score(400, shell, 0)
                if self.player.rect.x < shell.rect.x:
                    shell.x_vel = 10
                    shell.rect.x += 40 # 这里必须加的多 不然y collision又要把它停下来了
                    shell.direction = C.RIGHT
                else:
                    shell.x_vel = -10
                    shell.rect.x -= 40
                    shell.direction = C.LEFT
                shell.state = C.SHELL_SLIDE
        elif coin:
            setup.SOUNDS['coin'].play()
            self.update_score(100, coin, 1)
            coin.kill()

    def check_player_y_collisions(self):
        ground_step_pipe = pygame.sprite.spritecollideany(self.player, self.ground_step_pipe_group)
        brick = pygame.sprite.spritecollideany(self.player, self.brick_group)
        box = pygame.sprite.spritecollideany(self.player, self.box_group)
        enemy = pygame.sprite.spritecollideany(self.player, self.enemy_group)
        shell = pygame.sprite.spritecollideany(self.player, self.shell_group)

        if brick and box:
            brick, box = self.prevent_collision_conflict(brick, box)
        if brick:
            self.adjust_player_for_y_collisions(brick)
        elif box:
            self.adjust_player_for_y_collisions(box)
        elif ground_step_pipe:
            self.adjust_player_for_y_collisions(ground_step_pipe)
        elif enemy:
            if self.player.invincible:
                self.update_score(100, enemy, 0)
                self.enemy_group.remove(enemy)
                self.dying_group.add(enemy)
                direction = C.RIGHT if self.player.facing_right else C.LEFT
                enemy.start_death_jump(direction)
            elif self.player.y_vel > 0:
                enemy.state = C.JUMPED_ON
                setup.SOUNDS['stomp'].play()
                if enemy.name == C.GOOMBA:
                    self.update_score(100, enemy)
                    self.enemy_group.remove(enemy)
                    self.dying_group.add(enemy)
                elif enemy.name == C.KOOPA:
                    self.enemy_group.remove(enemy)
                    self.shell_group.add(enemy)
                self.player.rect.bottom = enemy.rect.top
                self.player.state = C.JUMP
                self.player.y_vel = -7
        # elif shell:
        #     if self.player.y_vel > 0:
        #         setup.SOUNDS['kick'].play()
        #         if shell.state != C.SHELL_SLIDE:
        #             if self.player.rect.centerx < shell.rect.centerx:
        #                 shell.direction = C.RIGHT
        #             else:
        #                 shell.direction = C.LEFT

        self.check_is_falling(self.player)
        self.check_entering_pipe(self.player)

    def prevent_collision_conflict(self, sprite1, sprite2):
        distance1 = abs(self.player.rect.centerx - sprite1.rect.centerx)
        distance2 = abs(self.player.rect.centerx - sprite2.rect.centerx)
        if distance1 > distance2:
            sprite1 = False
        else:
            sprite2 = False
        return sprite1, sprite2

    def adjust_player_for_x_collisions(self, sprite):
        # 如果不小心移动过头了可能有问题
        if self.player.rect.x < sprite.rect.x:
            self.player.rect.right = sprite.rect.left
        else:
            self.player.rect.left = sprite.rect.right
        self.player.x_vel = 0

    def adjust_player_for_y_collisions(self, sprite):
        # 从下往上撞
        if self.player.rect.top > sprite.rect.top:
            if sprite.name == C.MAP_BRICK:
                if not sprite.state == C.OPENED:
                    self.check_if_enemy_on(sprite)
                if sprite.state == C.RESTING:
                    if self.player.big and sprite.type == C.TYPE_NONE:
                        setup.SOUNDS['brick_smash'].play()
                        sprite.change_to_pieces(self.dying_group)
                    else:
                        setup.SOUNDS['bump'].play()
                        if sprite.type == C.TYPE_COIN:
                            self.update_score(200, sprite, 1)
                        sprite.start_bump()
            elif sprite.name == C.MAP_BOX:
                if not sprite.state == C.OPENED:
                    setup.SOUNDS['bump'].play()
                    self.check_if_enemy_on(sprite)
                if sprite.state == C.RESTING:
                    if sprite.type == C.TYPE_COIN:
                        self.update_score(200, sprite, 1)
                    sprite.start_bump()
            elif sprite.name == C.MAP_PIPE and sprite.type == C.PIPE_TYPE_HORIZONTAL:
                return
            self.player.y_vel = 7
            self.player.rect.top = sprite.rect.bottom
            self.player.state = C.FALL
        # 从上往下撞
        else:
            self.player.y_vel = 0
            self.player.rect.bottom = sprite.rect.top
            if self.player.state == C.FLAGPOLE:
                self.player.state = C.WALK_AUTO
            elif self.player.state == C.WALK_AUTO:
                self.player.state = C.WALK_AUTO
            else:
                self.player.state = C.WALK

    def check_if_enemy_on(self, sprite):
        sprite.rect.y -=5
        enemy = pygame.sprite.spritecollideany(sprite, self.enemy_group)
        if enemy:
            self.update_score(100, enemy, 0)
            self.enemy_group.remove(enemy)
            self.dying_group.add(enemy)
            if self.player.rect.centerx > sprite.rect.centerx:
                direction = C.LEFT
            else:
                direction = C.RIGHT
            enemy.start_death_jump(direction)
        sprite.rect.y += 5

    def in_frozen_state(self):
        if self.player.state in [C.SMALL_TO_BIG, C.BIG_TO_SMALL, C.BIG_TO_FIRE,
                                 C.FIRE_TO_SMALL, C.DEATH_JUMP, C.DOWN_TO_PIPE, C.UP_OUT_PIPE]:
            return True
        else:
            return False

    def check_is_falling(self, sprite):
        # 先试探性的往下走1 然后看看地上空不空，空的话往下掉
        sprite.rect.y += 1
        check_group = pygame.sprite.Group(self.ground_step_pipe_group, self.brick_group, self.box_group)
        if pygame.sprite.spritecollideany(sprite, check_group) is None:
            if sprite.state not in (C.JUMP, C.FLAGPOLE, C.WALK_AUTO) and not self.in_frozen_state():
                sprite.state = C.FALL
        sprite.rect.y -= 1

    def check_entering_pipe(self, sprite):
        self.player.rect.y += 1
        pipe = pygame.sprite.spritecollideany(self.player, self.pipe_group)
        if pipe and pipe.type == C.PIPE_TYPE_VERTICAL:
            if self.player.state == C.CROUCH and self.player.rect.x < pipe.rect.centerx and self.player.rect.right > pipe.rect.centerx:
                setup.SOUNDS['pipe'].play()
                self.player.state = C.DOWN_TO_PIPE
        self.player.rect.y -= 1

    def update_viewport(self):
        third = self.viewport.x + self.viewport.w//3
        if self.player.x_vel > 0 and self.player.rect.centerx > third and self.viewport.right < self.end_x:
            self.viewport.x += round(self.player.x_vel)
            self.start_x = self.viewport.x


    def draw(self, surface):
        self.level.blit(self.background, self.viewport, self.viewport)
        if self.player.state != C.IN_CASTLE:
            self.player_group.draw(self.level)
        self.static_coin_group.draw(self.level)
        self.coin_group.draw(self.level)
        self.powerup_group.draw(self.level)
        self.brick_group.draw(self.level)
        self.box_group.draw(self.level)
        self.enemy_group.draw(self.level)
        self.dying_group.draw(self.level)
        self.shell_group.draw(self.level)
        self.pipe_group.draw(self.level)
        self.flagpole_group.draw(self.level)
        self.score_group.draw(self.level)
        surface.blit(self.level, (0, 0), self.viewport)
        self.overhead_info.draw(surface)

    def check_for_player_death(self):
        if self.player.rect.y > C.SCREEN_H or self.overhead_info.time <= 0:
            self.player.start_death_jump()
            self.death_timer = self.current_time

    def update_score(self, score, sprite, coin_num=0):
        self.game_info[C.SCORE] += score
        if self.game_info[C.SCORE] > self.game_info[C.TOP_SCORE]:
            self.game_info[C.TOP_SCORE] = self.game_info[C.SCORE]
        self.game_info[C.COIN_TOTAL] += coin_num
        if self.game_info[C.COIN_TOTAL] == 100:
            self.game_info[C.COIN_TOTAL] = 0
            self.game_info[C.LIVES] += 1
        x = sprite.rect.x
        y = sprite.rect.y - 10
        self.score_group.add(stuff.Score(x, y, score))