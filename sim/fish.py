"""
Рыбы в аквариуме
"""

import pygame
import random
import math
import config


class Fish:
    """Класс рыбы"""
    
    def __init__(self, pos, world):
        self.pos = pygame.Vector2(pos)
        self.world = world
        
        # Скорость и ускорение
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(config.FISH_MAX_SPEED_MIN, config.FISH_MAX_SPEED_MAX)
        self.vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed * 0.5
        
        self.acc = pygame.Vector2(0, 0)
        
        # Параметры рыбы
        self.size = random.randint(0, 2)  # 0=маленькая, 1=средняя, 2=большая
        self.max_speed = random.uniform(config.FISH_MAX_SPEED_MIN, config.FISH_MAX_SPEED_MAX)
        self.max_force = random.uniform(config.FISH_MAX_FORCE_MIN, config.FISH_MAX_FORCE_MAX)
        
        self.energy = random.uniform(0.5, 1.0)
        self.panic = 0.0
        self.turn_bias = random.uniform(-0.3, 0.3)
        
        # Таймеры
        self.wander_angle = random.uniform(0, math.pi * 2)
        self.wander_change = 0
        
        # Индивидуальность для хаотичности
        self.chaos_factor = random.uniform(0.5, 1.5)  # Множитель хаотичности
        self.curiosity = random.uniform(0.3, 1.0)  # Любопытство (склонность к исследованию)
        self.school_tendency = random.uniform(0.5, 1.5)  # Склонность к стае
        
        # Тип поведения
        behavior_roll = random.random()
        cumulative = 0
        for i, prob in enumerate(config.BEHAVIOR_DISTRIBUTION):
            cumulative += prob
            if behavior_roll < cumulative:
                self.behavior_type = config.BEHAVIOR_TYPES[i]
                break
        else:
            self.behavior_type = 'school'  # По умолчанию
        
        # Здоровье и возраст
        self.health = 1.0
        self.age = 0.0  # Возраст в секундах
        self.is_alive = True
        
        # Цвет для визуального разнообразия
        self.color_variant = random.uniform(0.7, 1.3)  # Вариация цвета
        self.color_hue_shift = random.uniform(-0.3, 0.3)  # Сдвиг оттенка
        self.color_saturation = random.uniform(0.6, 1.0)  # Насыщенность
        
        # Направление (для спрайта)
        self.facing_right = self.vel.x >= 0
    
    def get_sprite(self):
        """Получить ASCII-спрайт рыбы в зависимости от размера и направления"""
        if self.size == 0:
            return config.SYMBOLS['fish_small_right'] if self.facing_right else config.SYMBOLS['fish_small_left']
        elif self.size == 1:
            return config.SYMBOLS['fish_medium_right'] if self.facing_right else config.SYMBOLS['fish_medium_left']
        else:
            return config.SYMBOLS['fish_right'] if self.facing_right else config.SYMBOLS['fish_left']
    
    def apply_force(self, force):
        """Применить силу к рыбе"""
        self.acc += force
    
    def seek(self, target, max_speed=None):
        """Вычислить силу для движения к цели"""
        if max_speed is None:
            max_speed = self.max_speed
        
        desired = target - self.pos
        dist = desired.length()
        
        if dist < 0.1:
            return pygame.Vector2(0, 0)
        
        desired = desired.normalize() * max_speed
        steer = desired - self.vel
        
        # Ограничить силу
        if steer.length() > self.max_force:
            steer = steer.normalize() * self.max_force
        
        return steer
    
    def wander(self):
        """Случайное блуждание с повышенной хаотичностью"""
        # Изменяем угол блуждания с учётом индивидуальности
        chaos = self.chaos_factor * random.uniform(-1.0, 1.0)
        self.wander_change += chaos * 0.3
        self.wander_angle += self.wander_change * (0.1 + self.curiosity * 0.1)
        
        # Периодические резкие изменения направления для хаотичности
        if random.random() < 0.02 * self.chaos_factor:
            self.wander_angle += random.uniform(-math.pi / 3, math.pi / 3)
        
        # Вычисляем желаемое направление с вариацией расстояния
        wander_distance = 50 + random.uniform(-20, 30) * self.curiosity
        wander_target = pygame.Vector2(
            math.cos(self.wander_angle),
            math.sin(self.wander_angle)
        ) * wander_distance
        
        wander_target += self.pos
        
        # Скорость блуждания зависит от индивидуальности
        wander_speed = self.max_speed * (0.3 + self.curiosity * 0.2)
        return self.seek(wander_target, wander_speed)
    
    def avoid_walls(self):
        """Избегание стен"""
        margin = 30
        force = pygame.Vector2(0, 0)
        
        # Левая стена
        if self.pos.x < margin:
            force.x += (margin - self.pos.x) / margin
        # Правая стена
        elif self.pos.x > self.world.width - margin:
            force.x -= (self.pos.x - (self.world.width - margin)) / margin
        
        # Верхняя стена
        if self.pos.y < margin:
            force.y += (margin - self.pos.y) / margin
        # Нижняя стена
        elif self.pos.y > self.world.height - margin:
            force.y -= (self.pos.y - (self.world.height - margin)) / margin
        
        if force.length() > 0:
            force = force.normalize() * self.max_force
            return self.seek(self.pos + force * 100)
        
        return pygame.Vector2(0, 0)
    
    def take_damage(self, amount):
        """Получить урон"""
        self.health = max(0.0, self.health - amount)
        if self.health <= config.FISH_MIN_HEALTH_TO_LIVE:
            self.is_alive = False
    
    def die(self):
        """Рыба умирает"""
        self.is_alive = False
        self.health = 0.0
    
    def update(self, dt, neighbors=None, food_list=None, water_quality=None):
        """
        Обновить состояние рыбы
        Силы уже применены к self.acc перед вызовом этого метода
        """
        if not self.is_alive:
            return
        
        # Увеличиваем возраст
        self.age += dt
        
        # Обновляем скорость на основе ускорения
        self.vel += self.acc * dt
        
        # Ограничиваем скорость (старые рыбы медленнее)
        age_speed_mult = max(0.7, 1.0 - self.age * 0.00001)
        max_speed = self.max_speed * age_speed_mult
        if self.vel.length() > max_speed:
            self.vel = self.vel.normalize() * max_speed
        
        # Демпфирование
        self.vel *= config.FISH_DAMPING
        
        # Обновляем позицию
        self.pos += self.vel * dt
        
        # Обновляем направление для спрайта
        if abs(self.vel.x) > 1:
            self.facing_right = self.vel.x >= 0
        
        # Уменьшаем энергию со временем (зависит от размера - большие рыбы тратят больше)
        energy_loss = dt * (0.01 + self.size * 0.005)
        self.energy = max(0.0, self.energy - energy_loss)
        
        # Урон от голода
        if self.energy < 0.2:
            self.take_damage(config.FISH_HUNGER_DAMAGE * dt)
        
        # Урон от плохого качества воды
        if water_quality:
            if water_quality.pollution > 0.7:
                pollution_damage = config.WATER_POLLUTION_DAMAGE * (water_quality.pollution - 0.7) / 0.3
                self.take_damage(pollution_damage * dt)
            if water_quality.oxygen < 0.3:
                oxygen_damage = config.WATER_POLLUTION_DAMAGE * (0.3 - water_quality.oxygen) / 0.3
                self.take_damage(oxygen_damage * dt)
        
        # Базовая потеря здоровья от возраста
        age_damage = config.FISH_AGE_FACTOR * self.age * dt
        self.take_damage(age_damage)
        
        # Базовая потеря здоровья
        self.take_damage(config.FISH_HEALTH_DECAY_RATE * dt)
        
        # Уменьшаем панику
        self.panic = max(0.0, self.panic - dt * 2)
        
        # Периодические случайные изменения направления для большей хаотичности
        if random.random() < 0.005 * self.chaos_factor:
            # Небольшой случайный поворот
            angle = math.atan2(self.vel.y, self.vel.x)
            angle += random.uniform(-0.3, 0.3) * self.chaos_factor
            speed = self.vel.length()
            self.vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
    
    def get_grid_pos(self, renderer):
        """Получить позицию в сетке"""
        gx, gy = renderer.pixel_to_grid(self.pos.x, self.pos.y)
        return gx, gy

