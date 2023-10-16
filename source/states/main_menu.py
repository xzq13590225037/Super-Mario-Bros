from .. import tools
from .. import constants as C
from .. import setup
from ..components import info
import pygame


class Menu(tools.State):
    def __init__(self):
        super(Menu, self).__init__()
        game_info = {
            C.COIN_TOTAL: 0,
            C.SCORE: 0,
            C.LIVES: 3,
            C.TOP_SCORE: 0,
            C.CURRENT_TIME: 0.,
            C.LEVEL_NUM: 1,
            C.PLAYER_NAME: C.MARIO,
            C.POWERUP_LEVEL: C.SMALL
        }
        self.startup(0.0, game_info)

    def startup(self, current_time, game_info):

        self.start_time = current_time
        self.next = C.LOAD_SCREEN
        self.game_info = game_info
        self.overhead_info = info.Info(self.game_info, C.MAIN_MENU)

        self.setup_background()
        self.setup_player()
        self.setup_cursor()

    def setup_background(self):
        self.background = setup.GRAPHICS['level_1']
        self.background_rect = self.background.get_rect()
        self.background = pygame.transform.scale(self.background, (int(self.background_rect.width * C.BG_MULTIPLIER),
                                                                   int(self.background_rect.height * C.BG_MULTIPLIER)))
        self.viewport = setup.SCREEN.get_rect()
        self.image_dict = {}
        image = tools.get_image(setup.GRAPHICS['title_screen'], 1, 60, 176, 88, (255, 0, 220), C.SIZE_MULTIPLIER) # 紫色
        rect = image.get_rect()
        rect.x, rect.y = (170, 100)
        self.image_dict['GAME_NAME_BOX'] = (image, rect)

    def setup_player(self):
        self.player_list = []
        player_rect_info = [(178, 32, 12, 16), (178, 128, 12, 16)]
        for rect_info in player_rect_info:
            image = tools.get_image(setup.GRAPHICS['mario_bros'], *rect_info, (0, 0, 0), C.PLAYER_MULTIPLIER)
            rect = image.get_rect()
            rect.x, rect.bottom = 110, C.GROUND_HEIGHT
            self.player_list.append((image, rect))
        self.player_index = 0

    def setup_cursor(self):
        self.cursor = pygame.sprite.Sprite()
        self.cursor.image = tools.get_image(setup.GRAPHICS['item_objects'], 24, 160, 8, 8, (0, 0, 0), 3)
        rect = self.cursor.image.get_rect()
        rect.x, rect.y = (220, 358)
        self.cursor.rect = rect
        self.cursor.state = C.PLAYER1

    def update(self, surface, keys, current_time):
        self.current_time = current_time
        self.game_info[C.CURRENT_TIME] = self.current_time
        self.player_image = self.player_list[self.player_index][0]
        self.player_rect = self.player_list[self.player_index][1]
        self.update_cursor(keys)
        self.overhead_info.update(self.game_info)

        surface.blit(self.background, self.viewport)
        surface.blit(self.image_dict['GAME_NAME_BOX'][0], self.image_dict['GAME_NAME_BOX'][1])
        surface.blit(self.player_image, self.player_rect)
        surface.blit(self.cursor.image, self.cursor.rect)
        self.overhead_info.draw(surface)

    def update_cursor(self, keys):
        if self.cursor.state == C.PLAYER1:
            self.cursor.rect.y = 358
            if keys[pygame.K_DOWN]:
                self.cursor.state = C.PLAYER2
                self.player_index = 1
                self.game_info[C.PLAYER_NAME] = C.LUIGI
        elif self.cursor.state == C.PLAYER2:
            self.cursor.rect.y = 403
            if keys[pygame.K_UP]:
                self.cursor.state = C.PLAYER1
                self.player_index = 0
                self.game_info[C.PLAYER_NAME] = C.MARIO
        if keys[pygame.K_RETURN]:
            self.reset_game_info()
            self.finished = True

    def reset_game_info(self):
        reset_info = {
            C.COIN_TOTAL: 0,
            C.SCORE: 0,
            C.LIVES: 3,
            C.CURRENT_TIME: 0.,
            C.LEVEL_NUM: 1,
            C.POWERUP_LEVEL: C.SMALL
        }
        self.game_info.update(reset_info)