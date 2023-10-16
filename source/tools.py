import pygame
import os
from abc import abstractmethod

keybinding = {
    'action': pygame.K_s,
    'jump': pygame.K_a,
    'left': pygame.K_LEFT,
    'right': pygame.K_RIGHT,
    'down': pygame.K_DOWN
}


# 游戏阶段的父类
class State:
    # 开始时间，当前时间，是否完结，下个阶段，持久数据
    def __init__(self):
        self.start_time = 0.0
        self.current_time = 0.0
        self.finished = False
        self.next = None
        self.game_info = {}

    # 两个抽象方法
    @abstractmethod
    def startup(self, current_time, game_info):
        pass

    def cleanup(self):
        self.finished = False
        return self.game_info

    # 最重要的更新方法
    @abstractmethod
    def update(self, surface, keys, current_time):
        pass


# 控制类
class Game:
    def __init__(self):
        self.screen = pygame.display.get_surface() # 不知道干嘛用的
        self.finished = False
        self.clock = pygame.time.Clock() # 启动时钟
        self.current_time = 0.0
        self.keys = pygame.key.get_pressed()
        self.state_dict = {}
        self.state_name = None
        self.state = None

    # 设置当前状态
    def setup_states(self, state_dict, start_state):
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]

    # 控制类的更新方法，会调用各自阶段的更新方法
    def update(self):
        self.current_time = pygame.time.get_ticks()
        if self.state.finished:
            self.next_state()
        self.state.update(self.screen, self.keys, self.current_time)

    def next_state(self):
        self.state_name = self.state.next
        game_info = self.state.cleanup()  # 感觉没啥用，直接self.state.finished = True 不就完事了？
        self.state = self.state_dict[self.state_name]
        self.state.startup(self.current_time, game_info)

    def run(self):
        while not self.finished:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.finished = True
                    pygame.display.quit()
                    quit()
                elif event.type == pygame.KEYDOWN:
                    self.keys = pygame.key.get_pressed()
                elif event.type == pygame.KEYUP:
                    self.keys = pygame.key.get_pressed()
            self.update()
            pygame.display.update()
            self.clock.tick(60) # 阻止游戏过快


# 载入图片，不知道为什么要放在这个文件里
def load_graphics(path, colorkey=(0, 0, 0), accept=('.jpg', '.png', '.bmp', '.gif')):
    graphics = {}
    for pic in os.listdir(path):
        name, ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pygame.image.load(os.path.join(path, pic))
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
                # img.set_colorkey(colorkey)
            graphics[name] = img
    return graphics


def get_image(sheet, x, y, width, height, colorkey, scale):
    image = pygame.Surface((width, height))
    image.blit(sheet, (0, 0), (x, y, width, height))
    image.set_colorkey(colorkey)
    image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
    # image = image.convert_alpha() # 可怕的关键代码 有点奇怪，PYGAME 2.0就会出错
    return image


def load_musics(path, accept=('.wav', '.mp3', '.ogg', '.mid')):
    musics = {}
    for music in os.listdir(path):
        name, ext = os.path.splitext(music)
        if ext.lower() in accept:
            musics[name] = os.path.join(path, music)
    return musics

def load_sounds(path, accept=('.wav','.mpe','.ogg','.mdi')):
    sounds = {}
    for sound in os.listdir(path):
        name, ext = os.path.splitext(sound)
        if ext.lower() in accept:
            sounds[name] = pygame.mixer.Sound(os.path.join(path, sound))
    return sounds
