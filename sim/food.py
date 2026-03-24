"""
Корм для рыб
"""

import pygame
import random
import config


class FoodPellet:
    """Класс корма"""
    
    def __init__(self, pos, world, delicious=False):
        self.pos = pygame.Vector2(pos)
        self.world = world
        
        # Параметры корма
        base_amount = random.uniform(config.FOOD_AMOUNT_MIN, config.FOOD_AMOUNT_MAX)
        base_ttl = random.uniform(config.FOOD_TTL_MIN, config.FOOD_TTL_MAX)
        
        if delicious:
            self.amount = base_amount * config.FOOD_DELICIOUS_MULTIPLIER
            self.spread = config.FOOD_SPREAD * config.FOOD_DELICIOUS_MULTIPLIER
            self.char = config.SYMBOLS['food_delicious']
        else:
            self.amount = base_amount
            self.spread = config.FOOD_SPREAD
            self.char = config.SYMBOLS['food']
        
        self.max_amount = self.amount
        self.ttl = base_ttl
        self.max_ttl = self.ttl
        
        # Скорость погружения
        self.sink_speed = random.uniform(config.FOOD_SINK_SPEED_MIN, config.FOOD_SINK_SPEED_MAX)
    
    def update(self, dt):
        """Обновить состояние корма"""
        # Тонет вниз
        self.pos.y += self.sink_speed * dt
        
        # Дрейф от течения (меньше чем у пузырьков)
        self.pos += self.world.current * dt * 0.1
        
        # Уменьшаем время жизни
        self.ttl -= dt
        
        # Постепенно уменьшаем количество (растворение)
        self.amount = max(0, self.amount - dt * (self.max_amount / self.max_ttl))
        
        # Удаляем если закончилось время или количество, или вышли за границы
        return (self.ttl > 0 and 
                self.amount > 0 and 
                self.pos.y < self.world.height + 50)
    
    def eat(self, amount):
        """Рыба съела часть корма"""
        self.amount = max(0, self.amount - amount)
    
    def get_grid_pos(self, renderer):
        """Получить позицию в сетке"""
        gx, gy = renderer.pixel_to_grid(self.pos.x, self.pos.y)
        return gx, gy

