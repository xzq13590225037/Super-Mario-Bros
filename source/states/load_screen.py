from .. import constants as C
from ..components import info
from .. import tools
from ..sound import Sound


class LoadScreen(tools.State):
    def __init__(self):
        tools.State.__init__(self)
        self.state = C.LOAD_SCREEN

    def startup(self, current_time, game_info):
        self.start_time = current_time
        self.game_info = game_info
        self.info_state = self.set_info_state()
        self.next = self.set_next_state()
        self.overhead_info = info.Info(self.game_info, self.info_state)
        self.sound = Sound(self.state)

    def set_next_state(self):
        return C.LEVEL

    def set_info_state(self):
        return C.LOAD_SCREEN

    def update(self, surface, keys, current_time):
        if current_time - self.start_time < 2400:
            surface.fill((0, 0, 0))
            self.overhead_info.update(self.game_info)
            self.overhead_info.draw(surface)
        # TODO 这里没写全黑和紫色
        else:
            self.finished = True


class GameOver(LoadScreen):
    def __init__(self):
        LoadScreen.__init__(self)
        self.state = C.GAME_OVER

    def set_next_state(self):
        return C.MAIN_MENU

    def set_info_state(self):
        return C.GAME_OVER

    def update(self, surface, keys, current_time):
        if current_time - self.start_time < 4000:
            surface.fill((0, 0, 0))
            self.overhead_info.update(self.game_info)
            self.overhead_info.draw(surface)
        # TODO 这里没写全黑和紫色
        else:
            self.finished = True


class TimeOut(LoadScreen):
    def __init__(self):
        LoadScreen.__init__(self)
        self.state = C.TIME_OUT

    def set_next_state(self):
        if self.game_info[C.LIVES] == 0:
            return C.GAME_OVER
        else:
            return C.LOAD_SCREEN

    def set_info_state(self):
        return C.TIME_OUT