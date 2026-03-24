"""
Конфигурация и параметры ASCII-аквариума
"""

# Размеры ASCII-сетки
COLS = 120
ROWS = 40

# Размер шрифта для рендеринга
FONT_SIZE = 16

# Параметры рыб
FISH_COUNT = 25
FISH_MAX_SPEED_MIN = 60
FISH_MAX_SPEED_MAX = 120
FISH_MAX_FORCE_MIN = 60
FISH_MAX_FORCE_MAX = 140
FISH_DAMPING = 0.995

# Радиусы boids
R_SEP = 25
R_ALIGN = 65
R_COH = 80

# Веса сил boids
W_SEP = 1.5
W_ALIGN = 0.8
W_COH = 0.6
W_WALL = 2.0
W_FOOD = 1.2
W_WANDER = 0.35  # Увеличено для большей хаотичности
W_CURRENT = 0.8

# Параметры корма
FOOD_TTL_MIN = 12
FOOD_TTL_MAX = 20
FOOD_AMOUNT_MIN = 8
FOOD_AMOUNT_MAX = 20
FOOD_SINK_SPEED_MIN = 5
FOOD_SINK_SPEED_MAX = 15
FOOD_SPREAD = 50
FOOD_EAT_RADIUS = 15
FOOD_PELLETS_PER_CLICK = 3
FOOD_DELICIOUS_MULTIPLIER = 2.0  # Множитель для вкусного корма

# Параметры пузырьков
BUBBLE_SPAWN_RATE = 0.02  # Вероятность спавна за кадр
BUBBLE_SPEED_MIN = 20
BUBBLE_SPEED_MAX = 40
BUBBLE_TTL_MIN = 3
BUBBLE_TTL_MAX = 8
BUBBLE_WIGGLE_AMPLITUDE = 2

# Параметры водорослей
SEAWEED_COUNT = 10
SEAWEED_HEIGHT_MIN = 10
SEAWEED_HEIGHT_MAX = 18
SEAWEED_AMPLITUDE = 4
SEAWEED_FREQ = 0.25
SEAWEED_SPEED = 2.0

# Параметры течения
CURRENT_MAX = 30
CURRENT_DAMPING = 0.98

# Цвета (RGB)
COLOR_MONOCHROME = {
    'background': (0, 0, 0),
    'fish': (255, 255, 255),
    'fish_small': (200, 200, 200),
    'fish_medium': (230, 230, 230),
    'fish_large': (255, 255, 255),
    'food': (200, 200, 200),
    'bubble': (150, 150, 150),
    'seaweed': (120, 120, 120),
    'decor': (100, 100, 100),
    'text': (255, 255, 255),
}

COLOR_COLORED = {
    'background': (0, 20, 40),
    'fish': (100, 200, 255),
    'fish_small': (120, 200, 255),  # Светло-голубой для маленьких
    'fish_medium': (80, 160, 240),  # Средний синий
    'fish_large': (60, 120, 220),  # Тёмно-синий для больших
    'food': (255, 220, 100),
    'bubble': (150, 220, 255),
    'seaweed': (30, 180, 60),  # Ярче зелёный
    'decor': (120, 100, 80),
    'text': (255, 255, 255),
}

COLOR_NIGHT = {
    'background': (5, 5, 15),
    'fish': (80, 120, 200),
    'fish_small': (120, 150, 220),
    'fish_medium': (80, 130, 200),
    'fish_large': (50, 100, 180),
    'food': (200, 180, 80),
    'bubble': (100, 150, 200),
    'seaweed': (20, 100, 40),
    'decor': (60, 50, 40),
    'text': (200, 200, 200),
}

# ASCII символы
SYMBOLS = {
    'fish_right': '><((((\'>',
    'fish_left': '<\')))))<>',
    'fish_small_right': '><>',
    'fish_small_left': '<><',
    'fish_medium_right': '><(((\'>',
    'fish_medium_left': '<\'))))<>',
    'food': '.',
    'food_delicious': '*',
    'bubble_small': 'o',
    'bubble_medium': 'O',
    'bubble_large': '°',
    'seaweed_stem': '|',
    'seaweed_wave': '~',
    'seaweed_leaf': 'Y',
    'rock': '#',
    'rock_alt': '@',
    'sand': ':',
}

# Spatial hash
SPATIAL_HASH_CELL_SIZE = 70  # Примерно R_align

# FPS
TARGET_FPS = 60

# Здоровье и выживание
FISH_HEALTH_DECAY_RATE = 0.0005  # Потеря здоровья в секунду (базовая)
FISH_HUNGER_DAMAGE = 0.015  # Урон от голода (energy < 0.2)
FISH_MIN_HEALTH_TO_LIVE = 0.1
FISH_AGE_FACTOR = 0.00005  # Влияние возраста на здоровье
FISH_STARVATION_TIME = 300  # Время до смерти от голода (секунды)

# Качество воды
WATER_POLLUTION_RATE = 0.0003  # Рост загрязнения в секунду (базовый)
WATER_POLLUTION_PER_FISH = 0.00008  # Загрязнение от каждой рыбы
WATER_OXYGEN_DECAY = 0.0002  # Уменьшение кислорода при загрязнении
WATER_CLEAN_AMOUNT = 0.4  # Сколько очищается за раз
WATER_CHANGE_AMOUNT = 0.9  # Эффект смены воды
WATER_POLLUTION_DAMAGE = 0.01  # Урон от загрязнения (при pollution > 0.7)

# Поведение
BEHAVIOR_TYPES = ['solitary', 'school', 'explorer']
BEHAVIOR_DISTRIBUTION = [0.3, 0.5, 0.2]  # Распределение типов
SOLITARY_COHESION_MULT = 0.2  # Множитель cohesion для одиночных
SOLITARY_ALIGN_MULT = 0.5  # Множитель alignment для одиночных
EXPLORER_WANDER_MULT = 1.8  # Множитель wander для исследователей
EXPLORER_COHESION_MULT = 0.7  # Множитель cohesion для исследователей

# Сохранение
AUTOSAVE_INTERVAL = 30  # секунды
SAVE_FILE = 'aquarium_state.json'

