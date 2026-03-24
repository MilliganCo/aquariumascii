"""
Пузырьки в аквариуме
"""

import pygame
import random
import math
import config


class Bubble:
    """Класс пузырька"""
    
    def __init__(self, pos, world):
        self.pos = pygame.Vector2(pos)
        self.world = world
        
        # Случайная скорость вверх
        speed = random.uniform(config.BUBBLE_SPEED_MIN, config.BUBBLE_SPEED_MAX)
        self.vel = pygame.Vector2(
            random.uniform(-config.BUBBLE_WIGGLE_AMPLITUDE, config.BUBBLE_WIGGLE_AMPLITUDE),
            -speed
        )
        
        self.ttl = random.uniform(config.BUBBLE_TTL_MIN, config.BUBBLE_TTL_MAX)
        self.max_ttl = self.ttl
        
        # Размер пузырька определяет символ
        size = random.random()
        if size < 0.4:
            self.char = config.SYMBOLS['bubble_small']
        elif size < 0.7:
            self.char = config.SYMBOLS['bubble_medium']
        else:
            self.char = config.SYMBOLS['bubble_large']
        
        self.phase = random.uniform(0, math.pi * 2)
    
    def update(self, dt):
        """Обновить позицию пузырька"""
        # Движение вверх
        self.pos += self.vel * dt
        
        # Дрейф от течения
        self.pos += self.world.current * dt * 0.3
        
        # Синусная качка
        self.phase += dt * 3
        self.pos.x += math.sin(self.phase) * dt * 5
        
        # Уменьшаем время жизни
        self.ttl -= dt
        
        return self.ttl > 0 and self.pos.y > -10
    
    def get_grid_pos(self, renderer):
        """Получить позицию в сетке"""
        gx, gy = renderer.pixel_to_grid(self.pos.x, self.pos.y)
        return gx, gy

