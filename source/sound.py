import pygame
from . import setup
from . import constants as C

class Sound:
    def __init__(self, game_state):
        self.sound_dict = setup.SOUNDS
        self.music_dict = setup.MUSICS
        self.game_state = game_state
        self.sound_state = C.NORMAL
        self.set_music_mix()

    def set_music_mix(self):
        if self.game_state == C.LEVEL:
            pygame.mixer.music.load(self.music_dict['main_theme'])
            pygame.mixer.music.play()
            self.sound_state = C.NORMAL
        elif self.game_state == C.GAME_OVER:
            pygame.mixer.music.load(self.music_dict['game_over'])
            pygame.mixer.music.play()
            self.sound_state = C.GAME_OVER

    def play_music(self, key, sound_state):
        pygame.mixer.music.load(self.music_dict[key])
        pygame.mixer.music.play()
        self.sound_state = sound_state

    def stop_music(self):
        pygame.mixer.music.stop()

    def update(self, player, time):

        if time == 100:
            self.play_music('out_of_time', C.TIME_WARNING)

        if self.sound_state == C.NORMAL:
            if player.dead:
                self.play_music('death', C.DEAD)
            elif player.invincible:
                self.play_music('invincible', C.INVINCIBLE)
            elif player.state == C.FLAGPOLE:
                self.play_music('flagpole', C.FLAGPOLE)
        elif self.sound_state == C.SPEED_UP:
            if player.dead:
                self.play_music('death', C.DEAD)
            elif player.invincible:
                self.play_music('invincible', C.INVINCIBLE)
            elif player.state == C.FLAGPOLE:
                self.play_music('flagpole', C.FLAGPOLE)
        elif self.sound_state == C.INVINCIBLE:
            if player.dead:
                self.play_music('death', C.DEAD)
            if not player.invincible:
                self.stop_music()
                self.play_music('main_theme', C.NORMAL)
        elif self.sound_state == C.TIME_WARNING:
            if not pygame.mixer.music.get_busy():
                self.play_music('main_theme_sped_up', C.SPEED_UP)
        elif self.sound_state == C.FLAGPOLE:
            if player.state == C.WALK_AUTO:
                self.play_music('stage_clear', C.STAGE_CLEAR)
        # elif self.sound_state == C.STAGE_CLEAR:
        #     if player.state == C.IN_CASTLE:
        #         self.sound_dict['count_down'].play()
        #         self.state = C.COUNT_DOWN
        # elif self.sound_state == C.COUNT_DOWN:
        #     if time == 0:
        #         self.sound_dict['count_down'].stop()



