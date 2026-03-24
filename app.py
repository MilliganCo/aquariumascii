"""
Главный файл ASCII-аквариума
"""

import pygame
import random
import sys
import math
from sim.world import World
from sim.fish import Fish
from sim.food import FoodPellet
from sim.bubble import Bubble
from sim.seaweed import Seaweed
from sim.boids import apply_boids_forces
from sim.spatial_hash import SpatialHash
from ui.ascii_grid import AsciiGrid
from ui.render import Renderer
from ui.care_panel import CarePanel
from save_system import save_aquarium_state, load_aquarium_state
import config


class AquariumApp:
    """Главный класс приложения"""
    
    def __init__(self):
        pygame.init()
        
        # Инициализация рендерера (создаст окно)
        self.renderer = Renderer()
        
        # Создаём мир в пиксельных координатах (соответствует размеру сетки)
        world_width = config.COLS * self.renderer.char_width
        world_height = (config.ROWS - 1) * self.renderer.char_height  # Минус строка статуса
        self.world = World(world_width, world_height)
        
        # Инициализация симуляции
        self.fish_list = []
        self.food_list = []
        self.bubble_list = []
        self.seaweed_list = []
        
        self.spatial_hash = SpatialHash(world_width, world_height)
        
        # Состояние приложения
        self.state = 'RUNNING'  # RUNNING, PAUSED, HELP_OVERLAY
        self.clock = pygame.time.Clock()
        self.fps = 0
        
        # Статистика ухода (должны быть установлены до загрузки)
        self.last_fed_time = 0.0
        self.show_care_panel = False
        
        # Попытка загрузить сохранённое состояние
        loaded = load_aquarium_state(self)
        
        # Инициализация если не загружено
        if not loaded:
            self._init_fish()
            self._init_seaweed()
            self._init_decor()
        else:
            # Водоросли и декор всегда инициализируем
            self._init_seaweed()
            self._init_decor()
        
        # Таймер автосохранения
        self.autosave_timer = 0.0
    
    def _init_fish(self):
        """Инициализировать рыб"""
        for _ in range(config.FISH_COUNT):
            pos = self.world.get_random_pos(margin=50)
            fish = Fish(pos, self.world)
            self.fish_list.append(fish)
    
    def _init_seaweed(self):
        """Инициализировать водоросли"""
        # Используем координаты сетки для размещения водорослей
        spacing = config.COLS / (config.SEAWEED_COUNT + 1)
        for i in range(config.SEAWEED_COUNT):
            # Конвертируем координаты сетки в пиксели
            grid_x = spacing * (i + 1)
            base_x = grid_x * self.renderer.char_width
            seaweed = Seaweed(base_x, self.world.height)
            self.seaweed_list.append(seaweed)
    
    def _init_decor(self):
        """Инициализировать декор дна (камни, песок)"""
        self.decor_rocks = []
        # Создаём несколько камней у дна
        for _ in range(5):
            x = random.uniform(0, self.world.width)
            y = self.world.height - random.uniform(0, 20)
            self.decor_rocks.append((x, y))
    
    def _add_fish(self, count=1):
        """Добавить рыб"""
        for _ in range(count):
            pos = self.world.get_random_pos(margin=50)
            fish = Fish(pos, self.world)
            self.fish_list.append(fish)
    
    def _remove_fish(self, count=1):
        """Удалить рыб"""
        for _ in range(min(count, len(self.fish_list))):
            if self.fish_list:
                self.fish_list.pop()
    
    def _spawn_food(self, pos, delicious=False):
        """Создать корм в позиции"""
        for _ in range(config.FOOD_PELLETS_PER_CLICK):
            offset = pygame.Vector2(
                random.uniform(-20, 20),
                random.uniform(-20, 20)
            )
            food = FoodPellet(pos + offset, self.world, delicious)
            self.food_list.append(food)
            
            # Создаём пузырьки при кормлении
            for _ in range(3):
                bubble_pos = pos + pygame.Vector2(
                    random.uniform(-15, 15),
                    random.uniform(-15, 15)
                )
                bubble = Bubble(bubble_pos, self.world)
                self.bubble_list.append(bubble)
    
    def _spawn_bubble(self):
        """Случайно создать пузырёк"""
        if random.random() < config.BUBBLE_SPAWN_RATE:
            # Спавн у дна или рядом с водорослями
            if random.random() < 0.5:
                # У дна
                pos = pygame.Vector2(
                    random.uniform(0, self.world.width),
                    self.world.height - random.uniform(0, 50)
                )
            else:
                # Рядом с водорослью
                if self.seaweed_list:
                    seaweed = random.choice(self.seaweed_list)
                    pos = pygame.Vector2(
                        seaweed.base_x + random.uniform(-10, 10),
                        self.world.height - random.uniform(5, 20)
                    )
                else:
                    return
            
            bubble = Bubble(pos, self.world)
            self.bubble_list.append(bubble)
    
    def _randomize_fish(self):
        """Рандомизировать позиции и скорости рыб"""
        for fish in self.fish_list:
            fish.pos = self.world.get_random_pos(margin=50)
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(config.FISH_MAX_SPEED_MIN, config.FISH_MAX_SPEED_MAX)
            fish.vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed * 0.5
    
    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == 'RUNNING':
                    mouse_pos = pygame.mouse.get_pos()
                    # Координаты мыши уже в пикселях окна, используем их напрямую
                    # Но ограничиваем область аквариума (без рамки и статуса)
                    world_x = max(0, min(mouse_pos[0], self.world.width))
                    world_y = max(0, min(mouse_pos[1], self.world.height))
                    world_pos = pygame.Vector2(world_x, world_y)
                    if event.button == 1:  # ЛКМ
                        self._spawn_food(world_pos, delicious=False)
                        self.last_fed_time = self.world.time
                    elif event.button == 3:  # ПКМ
                        self._spawn_food(world_pos, delicious=True)
                        self.last_fed_time = self.world.time
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    if self.state == 'HELP_OVERLAY':
                        self.state = 'RUNNING'
                    else:
                        self.state = 'HELP_OVERLAY'
                elif event.key == pygame.K_p:
                    if self.state == 'PAUSED':
                        self.state = 'RUNNING'
                    else:
                        self.state = 'PAUSED'
                elif event.key == pygame.K_n:
                    # Переключение ночного режима
                    current_mode = self.renderer.color_mode
                    if current_mode == 'night':
                        self.renderer.set_color_mode('colored')
                        self.world.set_night_mode(False)
                    elif current_mode == 'colored':
                        self.renderer.set_color_mode('monochrome')
                    else:  # monochrome
                        self.renderer.set_color_mode('night')
                        self.world.set_night_mode(True)
                elif event.key == pygame.K_m:
                    # Переключение между цветным и монохромным
                    current_mode = self.renderer.color_mode
                    if current_mode == 'monochrome':
                        self.renderer.set_color_mode('colored')
                    else:
                        self.renderer.set_color_mode('monochrome')
                elif event.key == pygame.K_r:
                    self._randomize_fish()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    self._add_fish(5)
                elif event.key == pygame.K_MINUS:
                    self._remove_fish(5)
                elif event.key == pygame.K_LEFTBRACKET:
                    self._remove_fish(1)
                elif event.key == pygame.K_RIGHTBRACKET:
                    self._add_fish(1)
                elif event.key == pygame.K_SPACE:
                    self.world.reset_current()
                elif event.key == pygame.K_c:
                    # Очистка аквариума
                    if self.state == 'RUNNING':
                        self.world.water_quality.clean()
                elif event.key == pygame.K_w:
                    # Смена воды
                    if self.state == 'RUNNING':
                        self.world.water_quality.change_water()
                elif event.key == pygame.K_f:
                    # Добавить рыбу
                    if self.state == 'RUNNING':
                        self._add_fish(1)
                elif event.key == pygame.K_TAB:
                    # Показать/скрыть панель ухода
                    self.show_care_panel = not self.show_care_panel
        
        # Обработка клавиш для течения (зажатые)
        # Используем стрелки или другие клавиши для течения, чтобы не конфликтовать с W (смена воды)
        if self.state == 'RUNNING':
            keys = pygame.key.get_pressed()
            current_dx = 0
            current_dy = 0
            
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                current_dx -= config.CURRENT_MAX
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                current_dx += config.CURRENT_MAX
            if keys[pygame.K_UP]:
                current_dy -= config.CURRENT_MAX * 0.5
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                current_dy += config.CURRENT_MAX * 0.5
            
            if current_dx != 0 or current_dy != 0:
                self.world.set_current(current_dx, current_dy)
        
        return True
    
    def update(self, dt):
        """Обновить симуляцию"""
        if self.state != 'RUNNING':
            return
        
        # Обновляем мир (передаём количество рыб для качества воды)
        self.world.update(dt, len(self.fish_list))
        
        # Обновляем spatial hash
        self.spatial_hash.clear()
        for fish in self.fish_list:
            self.spatial_hash.insert(fish, fish.pos)
        
        # Обновляем рыб
        for fish in self.fish_list:
            # Получаем соседей через spatial hash
            neighbors = self.spatial_hash.get_neighbors(fish.pos, config.R_COH)
            # Убираем саму рыбу из списка соседей
            neighbors = [n for n in neighbors if n != fish]
            
            # Сбрасываем ускорение
            fish.acc = pygame.Vector2(0, 0)
            
            # Применяем базовые силы (wander, wall avoidance, течение)
            # Увеличиваем wander для большей хаотичности
            wander_multiplier = 1.0 + fish.chaos_factor * 0.3
            fish.apply_force(fish.wander() * config.W_WANDER * wander_multiplier)
            fish.apply_force(fish.avoid_walls() * config.W_WALL)
            fish.apply_force(fish.world.current * config.W_CURRENT)
            
            # Применяем boids силы
            apply_boids_forces(fish, neighbors, self.food_list)
            
            # Обновляем рыбу (применяет ускорение к скорости и обновляет позицию)
            fish.update(dt, neighbors, self.food_list, self.world.water_quality)
            
            # Проверяем поедание корма
            for food in self.food_list[:]:
                dist = (fish.pos - food.pos).length()
                if dist < config.FOOD_EAT_RADIUS:
                    eat_amount = min(2.0, food.amount)
                    food.eat(eat_amount)
                    fish.energy = min(1.0, fish.energy + eat_amount * 0.1)
                    # Кормление восстанавливает немного здоровья
                    fish.health = min(1.0, fish.health + eat_amount * 0.05)
        
        # Удаляем мёртвых рыб
        dead_fish = [f for f in self.fish_list if not f.is_alive]
        for fish in dead_fish:
            # Эффект при смерти - пузырьки
            for _ in range(5):
                bubble = Bubble(fish.pos, self.world)
                self.bubble_list.append(bubble)
        self.fish_list = [f for f in self.fish_list if f.is_alive]
        
        # Обновляем корм
        self.food_list = [f for f in self.food_list if f.update(dt)]
        
        # Обновляем пузырьки
        self.bubble_list = [b for b in self.bubble_list if b.update(dt)]
        
        # Спавн новых пузырьков
        self._spawn_bubble()
        
        # Автосохранение
        self.autosave_timer += dt
        if self.autosave_timer >= config.AUTOSAVE_INTERVAL:
            save_aquarium_state(self)
            self.autosave_timer = 0.0
    
    def render(self):
        """Отрисовать кадр"""
        # Создаём ASCII-сетку
        grid = AsciiGrid()
        
        # Рисуем рамку
        self.renderer.render_frame(grid)
        
        # Рисуем декор дна (песок) - статичный паттерн
        decor_color = self.renderer.get_color('decor')
        sand_y = config.ROWS - 2
        for x in range(1, config.COLS - 1, 3):  # Каждые 3 клетки
            grid.set_char(x, sand_y, config.SYMBOLS['sand'], decor_color)
        
        # Рисуем камни (используем фиксированный паттерн для видимости)
        for i, (rock_x, rock_y) in enumerate(self.decor_rocks):
            gx, gy = self.renderer.pixel_to_grid(rock_x, rock_y)
            if 0 < gx < config.COLS - 1 and sand_y - 2 < gy < config.ROWS - 1:
                char = config.SYMBOLS['rock'] if i % 2 == 0 else config.SYMBOLS['rock_alt']
                grid.set_char(gx, gy, char, decor_color)
        
        # Рисуем водоросли
        seaweed_color = self.renderer.get_color('seaweed')
        for seaweed in self.seaweed_list:
            seaweed.render_to_grid(grid, self.world.time, self.renderer, seaweed_color)
        
        # Рисуем корм
        for food in self.food_list:
            gx, gy = food.get_grid_pos(self.renderer)
            color = self.renderer.get_color('food')
            grid.set_char(gx, gy, food.char, color)
        
        # Рисуем пузырьки
        for bubble in self.bubble_list:
            gx, gy = bubble.get_grid_pos(self.renderer)
            color = self.renderer.get_color('bubble')
            grid.set_char(gx, gy, bubble.char, color)
        
        # Рисуем рыб (поверх всего) с разными цветами по размеру и типу поведения
        for fish in self.fish_list:
            gx, gy = fish.get_grid_pos(self.renderer)
            sprite = fish.get_sprite()
            
            # Выбираем базовый цвет в зависимости от размера рыбы
            if fish.size == 0:
                base_color = self.renderer.get_color('fish_small')
            elif fish.size == 1:
                base_color = self.renderer.get_color('fish_medium')
            else:
                base_color = self.renderer.get_color('fish_large')
            
            # Применяем вариацию цвета для индивидуальности
            color = list(base_color)
            
            # Изменяем цвет в зависимости от типа поведения
            if fish.behavior_type == 'solitary':
                # Одиночные - более зелёные оттенки
                color[0] = int(color[0] * 0.7)  # Уменьшаем красный
                color[1] = int(color[1] * 1.2)  # Увеличиваем зелёный
            elif fish.behavior_type == 'explorer':
                # Исследователи - более жёлтые/оранжевые оттенки
                color[0] = int(color[0] * 1.3)  # Увеличиваем красный
                color[1] = int(color[1] * 1.1)  # Немного увеличиваем зелёный
                color[2] = int(color[2] * 0.8)  # Уменьшаем синий
            
            # Применяем индивидуальную вариацию
            color[0] = int(color[0] * fish.color_variant)
            color[1] = int(color[1] * fish.color_variant)
            color[2] = int(color[2] * fish.color_variant)
            
            # Применяем сдвиг оттенка
            if fish.color_hue_shift > 0:
                # Сдвиг в сторону красного/жёлтого
                color[0] = int(color[0] * (1.0 + fish.color_hue_shift))
                color[2] = int(color[2] * (1.0 - fish.color_hue_shift * 0.5))
            else:
                # Сдвиг в сторону синего/зелёного
                color[1] = int(color[1] * (1.0 - fish.color_hue_shift))
                color[2] = int(color[2] * (1.0 - fish.color_hue_shift))
            
            # Применяем насыщенность
            for i in range(3):
                color[i] = int(color[i] * fish.color_saturation + 255 * (1 - fish.color_saturation) * 0.3)
            
            # Ограничиваем диапазон
            color = tuple(max(0, min(255, c)) for c in color)
            
            grid.set_string(gx, gy, sprite, color)
        
        # Рисуем статусную строку
        stats = {
            'fish_count': len(self.fish_list),
            'food_count': len(self.food_list),
            'current_x': self.world.current.x,
            'current_y': self.world.current.y,
            'fps': self.fps,
            'mode': self.state
        }
        self.renderer.render_status_bar(grid, stats)
        
        # Рисуем подсказки если нужно
        if self.state == 'HELP_OVERLAY':
            self.renderer.render_help_overlay(grid)
        
        # Рисуем панель ухода если включена
        if self.show_care_panel:
            CarePanel.render_to_grid(grid, self.world, self.fish_list, self.last_fed_time)
        
        # Рендерим сетку
        self.renderer.render_grid(grid)
        self.renderer.update()
    
    def run(self):
        """Главный цикл"""
        running = True
        
        while running:
            dt = self.clock.tick(config.TARGET_FPS) / 1000.0  # Конвертируем в секунды
            self.fps = self.clock.get_fps()
            
            running = self.handle_events()
            self.update(dt)
            self.render()
        
        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    app = AquariumApp()
    app.run()

