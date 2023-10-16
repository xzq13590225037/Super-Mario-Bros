CAPTION = 'SUPERMARIO PYTHON VERSION'

SCREEN_W, SCREEN_H = 800, 600
SCREEN_SIZE = (SCREEN_W, SCREEN_H)
GROUND_HEIGHT = SCREEN_H - 62

# COLORS
BGCOLOR = 'WHITE'
BLUE = (92, 148, 252)
ORANGE = (255, 128, 0)

BG_MULTIPLIER = 2.679
SIZE_MULTIPLIER = 2.5
PLAYER_MULTIPLIER = 2.9
INFO_MULTIPLIER = 2.9
BACKGROUND_MULTIPLIER = 2.679
BRICK_SIZE_MULTIPLIER = 2.69

GAME_TIMEOUT = 301

# GAME STATES
MAIN_MENU = 'main menu'
LOAD_SCREEN = 'load screen'
TIME_OUT = 'time out'
GAME_OVER = 'game over'
LEVEL = 'level'

# GAME INFO
COIN_TOTAL = 'coin_total'
SCORE = 'score'
TOP_SCORE = 'top score'
LIVES = 'lives'
CURRENT_TIME = 'current time'
LEVEL_NUM = 'level num'
PLAYER_NAME = 'player name'
POWERUP_LEVEL = 'powerup level'
MARIO = 'mario'
LUIGI = 'luigi'

# MAP COMPONENTS
MAP_IMAGE = 'image_name'
MAP_MAPS = 'maps'
SUB_MAP = 'sub_map'
MAP_GROUND = 'ground'
MAP_PIPE = 'pipe'
MAP_STEP = 'step'
MAP_SLIDER = 'slider'
MAP_COIN = 'coin'
MAP_BRICK = 'brick'
MAP_BOX = 'box'
MAP_FLAGPOLE = 'flagpole'
PIPE_TYPE_NORMAL = 0
PIPE_TYPE_VERTICAL = 1
PIPE_TYPE_HORIZONTAL = 2
TYPE_NONE = 0 # 砖块类型
TYPE_COIN = 1
TYPE_STAR = 2
TYPE_MUSHROOM = 3
TYPE_FIREFLOWER = 4
TYPE_FIREBALL = 5
TYPE_LIFEMUSHROOM = 6
MAP_ENEMY = 'enemy'
MAP_CHECKPOINT = 'checkpoint'
ENEMY_GROUPID = 'enemy_groupid'
MAP_INDEX = 'map_index'
CHECKPOINT_TYPE_ENEMY = 0
CHECKPOINT_TYPE_FLAG = 1
CHECKPOINT_TYPE_CASTLE = 2
CHECKPOINT_TYPE_MUSHROOM = 3
CHECKPOINT_TYPE_PIPE = 4        # trigger player to go right in a pipe
CHECKPOINT_TYPE_PIPE_UP = 5     # trigger player to another map and go up out of a pipe
CHECKPOINT_TYPE_MAP = 6         # trigger player to go to another map
CHECKPOINT_TYPE_BOSS = 7        # defeat the boss
FLAGPOLE_TYPE_FLAG = 0
FLAGPOLE_TYPE_POLE = 1
FLAGPOLE_TYPE_TOP = 2
BRICK_NUM = 'brick_num'
DIRECTION = 'direction'
HORIZONTAL = 0
VERTICAL = 1


# COMPONENT COLOR
COLOR = 'color'
COLOR_TYPE_ORANGE = 0
COLOR_TYPE_GREEN = 1
COLOR_TYPE_RED = 2

# BRICK STATES
RESTING = 'resting'
BUMPED = 'bumped'
OPENED = 'opened'

# MUSHROOM STATES
REVEAL = 'reveal'
SLIDE = 'slide'

# FIREBALL STATES
FLYING = 'flying'
BOUNCING = 'bouncing'
EXPLODING = 'exploding'

# STAR STATES
BOUNCING = 'bouncing'

# PLAYER FRAMES
PLAYER_FRAMES = 'image_frames'
RIGHT_SMALL_NORMAL = 'right_small_normal'
RIGHT_BIG_NORMAL = 'right_big_normal'
RIGHT_BIG_FIRE = 'right_big_fire'

# PLAYER STATES
STAND = 'stand'
WALK = 'walk'
JUMP = 'jump'
FALL = 'fall'
FLY = 'fly'
CROUCH = 'crouch'
SMALL_TO_BIG = 'small to big'
BIG_TO_SMALL = 'big to small'
BIG_TO_FIRE = 'big to fire'
FIRE_TO_SMALL = 'fire to small'
FLAGPOLE = 'flag pole'
WALK_AUTO = 'walk auto'
END_OF_LEVEL_FALL = 'end of level fall'
IN_CASTLE = 'in castle'
DOWN_TO_PIPE = 'down to pipe'
UP_OUT_PIPE = 'up out of pipe'
SMALL = 'small'
BIG = 'big'
ON_FIRE = 'on fire'

# FLAG STATES
TOP_OF_POLE = 'top of pole'
SLIDE_DOWN = 'slide down'
BOTTOM_OF_POLE = 'bottom of pole'

# PLAYER FORCES
PLAYER_SPEED = 'speed'
MAX_WALK_SPEED = "max_walk_speed"
MAX_RUN_SPEED = "max_run_speed"
MAX_Y_VEL = "max_y_velocity"
WALK_ACCEL = 'walk_accel'
RUN_ACCEL = "run_accel"
JUMP_VEL = "jump_velocity"

# 不知道下面着三个家伙干嘛的
SMALL_TURNAROUND = .35
JUMP_GRAVITY = .31
GRAVITY = 1.01

# MAIN MENU CURSOR STATES
PLAYER1 = '1 PLAYER GAME'
PLAYER2 = '2 PLAYER GAME'

# LIST OF ENEMIES
GOOMBA = 'goomba'
KOOPA = 'koopa'
FLY_KOOPA = 'fly koopa'
FIRE_KOOPA = 'fire koopa'
FIRE = 'fire'
PIRANHA = 'piranha'
FIRESTICK = 'firestick'

ENEMY_TYPE_GOOMBA = 0
ENEMY_TYPE_KOOPA = 1
ENEMY_TYPE_FLY_KOOPA = 2
ENEMY_TYPE_PIRANHA = 3
ENEMY_TYPE_FIRESTICK = 4
ENEMY_TYPE_FIRE_KOOPA = 5
ENEMY_RANGE = 'range'

LEFT = 'left'
RIGHT = 'right'
JUMPED_ON = 'jumped on'
DEATH_JUMP = 'death jump'

# KOOPA STATES
SHELL_SLIDE = 'shell slide'

# SOUND STATES
NORMAL = 'normal'
STAGE_CLEAR = 'stage clear'
WORLD_CLEAR = 'world clear'
TIME_WARNING = 'time warning'
INVINCIBLE = 'invincible'
SPEED_UP = 'speed up'
DEAD = 'dead'
COUNT_DOWN = 'count_down'