from .. import constants as C
from .. import tools
from .. import setup
from .coin import FlashingCoin
import pygame


class Character(pygame.sprite.Sprite):
    def __init__(self, image):
        super(Character, self).__init__()
        self.image = image
        self.rect = self.image.get_rect()


class Info:
    def __init__(self, game_info, state):
        self.coin_total = game_info[C.COIN_TOTAL]
        self.total_lives = game_info[C.LIVES]
        self.state = state # 某个阶段
        self.game_info = game_info
        self.image_dict = {}

        self.create_font_image_dict() # 把每个字符对应的图片及大小放到字典里
        self.create_info_labels() # 有点奇怪 为什么是游戏初始的状态
        self.create_state_labels()
        self.flashing_coin = FlashingCoin(280, 53)

    def create_font_image_dict(self):
        char_rect_list = [# 0 - 9
                           (3, 230, 7, 7), (12, 230, 7, 7), (19, 230, 7, 7),
                           (27, 230, 7, 7), (35, 230, 7, 7), (43, 230, 7, 7),
                           (51, 230, 7, 7), (59, 230, 7, 7), (67, 230, 7, 7),
                           (75, 230, 7, 7),
                           # A - Z
                           (83, 230, 7, 7), (91, 230, 7, 7), (99, 230, 7, 7),
                           (107, 230, 7, 7), (115, 230, 7, 7), (123, 230, 7, 7),
                           (3, 238, 7, 7), (11, 238, 7, 7), (20, 238, 7, 7),
                           (27, 238, 7, 7), (35, 238, 7, 7), (44, 238, 7, 7),
                           (51, 238, 7, 7), (59, 238, 7, 7), (67, 238, 7, 7),
                           (75, 238, 7, 7), (83, 238, 7, 7), (91, 238, 7, 7),
                           (99, 238, 7, 7), (108, 238, 7, 7), (115, 238, 7, 7),
                           (123, 238, 7, 7), (3, 246, 7, 7), (11, 246, 7, 7),
                           (20, 246, 7, 7), (27, 246, 7, 7), (48, 246, 7, 7),
                           # -*
                           (68, 249, 6, 2), (75, 247, 6, 6)]
        char_string = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ -*'

        for char, rect in zip(char_string, char_rect_list):
            self.image_dict[char] = tools.get_image(setup.GRAPHICS['text_images'], *rect, C.BLUE, C.INFO_MULTIPLIER)

    def create_info_labels(self):
        self.score_text = []
        self.coin_count_text = []
        self.player_label = []
        self.luigi_label = []
        self.world_label = []
        self.time_label = []
        self.stage_label = []


        self.create_label(self.score_text, '000000', 75, 55)
        self.create_label(self.coin_count_text, '*00', 300, 55)
        # MARIO OR LUIGI
        self.create_label(self.player_label, self.game_info[C.PLAYER_NAME].upper(), 75, 30)
        self.create_label(self.world_label, 'WORLD', 450, 30)
        self.create_label(self.time_label, 'TIME', 625, 30)
        self.create_label(self.stage_label, '1-1', 472, 55)

        self.info_labels = [
            self.score_text,
            self.coin_count_text,
            self.player_label,
            self.world_label,
            self.time_label,
            self.stage_label,
        ]

    def create_state_labels(self):
        if self.state == C.MAIN_MENU:
            self.create_main_menu_labels()
        elif self.state == C.LOAD_SCREEN:
            self.create_player_image()
            self.create_load_screen_labels()
        elif self.state == C.LEVEL:
            self.create_level_labels()
        elif self.state == C.GAME_OVER:
            self.create_player_image()
            self.create_game_over_labels()
        elif self.state == C.TIME_OUT:
            self.create_time_out_labels()

    def create_player_image(self):
        # 为了显示x
        self.life_times_image = tools.get_image(setup.GRAPHICS['text_images'], 75, 247, 6, 6, (92, 148, 252), 2.9)
        self.life_times_rect = self.life_times_image.get_rect(center=(387, 295))

        if self.game_info[C.PLAYER_NAME] == C.MARIO:
            self.player_image = tools.get_image(setup.GRAPHICS['mario_bros'], 178, 32, 12, 16, (92, 148, 252), C.PLAYER_MULTIPLIER)
        else:
            self.player_image = tools.get_image(setup.GRAPHICS['mario_bros'], 178, 128, 12, 16, (92, 148, 252), C.PLAYER_MULTIPLIER)
        self.player_rect = self.player_image.get_rect(center=(320, 290))

    def create_load_screen_labels(self):
        self.world_label = []
        self.stage_label2 = []
        self.life_total_label = []
        self.create_label(self.world_label, 'WORLD', 280, 200)
        self.create_label(self.stage_label2, '1-1', 430, 200)
        self.create_label(self.life_total_label, str(self.total_lives), 450, 285)
        self.state_labels = [self.world_label, self.stage_label2, *self.info_labels, self.life_total_label]

    def create_main_menu_labels(self):
        self.mario_game = []
        self.luigi_game = []
        self.top = []
        self.top_score = []

        self.create_label(self.mario_game, C.PLAYER1, 272, 360)
        self.create_label(self.luigi_game, C.PLAYER2, 272, 405)
        self.create_label(self.top, 'TOP - ', 290, 465)
        self.create_label(self.top_score, '000000', 400, 465)
        self.state_labels = [self.mario_game, self.luigi_game, self.top, self.top_score, *self.info_labels]

    def create_level_labels(self):
        self.time = C.GAME_TIMEOUT
        self.current_time = 0
        self.clock_time_label = []
        # 啥时候更新时间呢？ 答案 handle level state
        self.create_label(self.clock_time_label, str(self.time), 645, 55)
        self.state_labels = [self.clock_time_label, *self.info_labels]

    def create_game_over_labels(self):
        self.gameover_label = []
        self.create_label(self.gameover_label, 'GAME  OVER', 280, 300)
        self.state_labels = [self.gameover_label, *self.info_labels]

    def create_timeout_labels(self):
        self.timeout_label = []
        self.create_label(self.timeout_label, 'TIME OUT', 290, 310)
        self.state_labels = [self.timeout_label, *self.info_labels]

    # 接受一个列表和文字，返回存满文字SPIRITE的列表
    def create_label(self, label_list, string, x, y):
        for letter in string:
            label_list.append(Character(self.image_dict[letter]))
        self.set_label_rect(label_list, x, y)

    def set_label_rect(self, label_list, x, y):
        for i, letter in enumerate(label_list):
            letter.rect.x = x + (letter.rect.width + 3) * i
            letter.rect.y = y
            if letter.image == self.image_dict['-']:
                letter.rect.y += 7
                letter.rect.x += 2

    def update(self, game_info):
        self.handle_level_state(game_info)

    def handle_level_state(self, game_info):
        self.score = game_info[C.SCORE]
        self.update_text(self.score_text, self.score)
        self.update_text(self.coin_count_text, game_info[C.COIN_TOTAL])
        self.update_text(self.stage_label, game_info[C.LEVEL_NUM])
        if self.state == C.MAIN_MENU:
            self.update_text(self.top_score, game_info[C.TOP_SCORE])
        elif self.state == C.LOAD_SCREEN:
          self.update_text(self.stage_label2, game_info[C.LEVEL_NUM])
        elif self.state == C.LEVEL:
            if (game_info[C.CURRENT_TIME] - self.current_time) > 1000:
                self.current_time = game_info[C.CURRENT_TIME]
                self.time -= 1
                self.update_text(self.clock_time_label, self.time, True)
        self.flashing_coin.update(game_info)

    def update_text(self, label, value, reset=False):
        if reset and len(label) > len(str(value)):
            label.remove(label[0])
        index = len(label) - 1
        for digit in reversed(str(value)):
            rect = label[index].rect
            label[index] = Character(self.image_dict[digit])
            label[index].rect = rect
            index -= 1

    def draw(self, surface):
        for label in self.state_labels:
            for letter in label:
                surface.blit(letter.image, letter.rect)
        if self.state == C.LOAD_SCREEN:
            surface.blit(self.player_image, self.player_rect)
            surface.blit(self.life_times_image, self.life_times_rect)

        surface.blit(self.flashing_coin.image, self.flashing_coin.rect)
