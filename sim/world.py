"""
Глобальное окружение аквариума
"""

import pygame
import random
import config
from sim.water_quality import WaterQuality


class World:
    """Класс для управления глобальным состоянием мира"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.bounds = pygame.Rect(0, 0, width, height)
        self.current = pygame.Vector2(0, 0)  # Течение
        self.light_level = 1.0  # 0.0 = ночь, 1.0 = день
        self.noise_seed = random.random() * 1000
        self.time = 0.0
        self.water_quality = WaterQuality()
    
    def update(self, dt, fish_count=0):
        """Обновить состояние мира"""
        self.time += dt
        # Течение постепенно затухает
        self.current *= config.CURRENT_DAMPING
        # Обновляем качество воды
        self.water_quality.update(dt, fish_count)
    
    def set_current(self, dx, dy):
        """Установить течение"""
        self.current.x = max(-config.CURRENT_MAX, min(config.CURRENT_MAX, dx))
        self.current.y = max(-config.CURRENT_MAX, min(config.CURRENT_MAX, dy))
    
    def reset_current(self):
        """Сбросить течение"""
        self.current = pygame.Vector2(0, 0)
    
    def set_night_mode(self, enabled):
        """Включить/выключить ночной режим"""
        self.light_level = 0.3 if enabled else 1.0
    
    def get_random_pos(self, margin=10):
        """Получить случайную позицию внутри границ"""
        return pygame.Vector2(
            random.uniform(margin, self.width - margin),
            random.uniform(margin, self.height - margin)
        )

