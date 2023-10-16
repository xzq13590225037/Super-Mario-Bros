import pygame
from source import constants as C
from source.states import main_menu, load_screen, level
from source import tools


def main():
    game = tools.Game() # 初始主控流程
    # 初始各个游戏阶段
    state_dict = {C.MAIN_MENU: main_menu.Menu(),
                  C.LOAD_SCREEN: load_screen.LoadScreen(),
                  C.LEVEL: level.Level(),
                  C.GAME_OVER: load_screen.GameOver(),
                  C.TIME_OUT: load_screen.TimeOut()
                  }
    # 启动主菜单
    game.setup_states(state_dict, C.MAIN_MENU)

    # 执行主控流程里的主函数
    game.run()


# 主入口
if __name__ == '__main__':
    main()





