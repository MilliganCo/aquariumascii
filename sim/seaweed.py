"""
Водоросли в аквариуме
"""

import math
import random
import config


class Seaweed:
    """Класс водоросли"""
    
    def __init__(self, base_x, world_height):
        self.base_x = base_x
        self.world_height = world_height
        self.height = random.randint(config.SEAWEED_HEIGHT_MIN, config.SEAWEED_HEIGHT_MAX)
        self.phase = random.uniform(0, math.pi * 2)
        self.amplitude = config.SEAWEED_AMPLITUDE
        self.freq = config.SEAWEED_FREQ
        self.speed = config.SEAWEED_SPEED
    
    def get_x_at_y(self, y, time):
        """
        Получить x-координату водоросли на высоте y
        y - высота от дна (0 = дно, height = верхушка)
        """
        # Инвертируем y (0 = дно, height = верх)
        normalized_y = y / self.height if self.height > 0 else 0
        offset = math.sin(self.phase + normalized_y * self.freq + time * self.speed) * self.amplitude
        return self.base_x + offset
    
    def render_to_grid(self, grid, time, renderer, color=None):
        """Отрисовать водоросль в сетку"""
        # Конвертируем base_x в координаты сетки
        base_gx, base_gy_bottom = renderer.pixel_to_grid(self.base_x, self.world_height)
        
        # Убеждаемся, что base_gx в пределах сетки
        if base_gx < 1:
            base_gx = 1
        elif base_gx >= config.COLS - 1:
            base_gx = config.COLS - 2
        
        # Рисуем стебель снизу вверх (в координатах сетки)
        for y_offset in range(self.height):
            # Вычисляем смещение по x с учётом анимации
            normalized_y = y_offset / self.height if self.height > 0 else 0
            offset_x = math.sin(self.phase + normalized_y * self.freq + time * self.speed) * self.amplitude
            offset_gx = int(offset_x / renderer.char_width)
            
            gx = base_gx + offset_gx
            gy = base_gy_bottom - y_offset  # Идём вверх от дна
            
            # Выбираем символ
            if y_offset == self.height - 1:
                # Верхушка - листочек
                char = config.SYMBOLS['seaweed_leaf']
            elif y_offset % 3 == 0:
                # Периодически волна
                char = config.SYMBOLS['seaweed_wave']
            else:
                # Обычный стебель
                char = config.SYMBOLS['seaweed_stem']
            
            # Проверяем границы более строго (не рисуем на границах и статусе)
            if 1 <= gx < config.COLS - 1 and 1 <= gy < config.ROWS - 2:
                grid.set_char(gx, gy, char, color)

