"""
Рендеринг ASCII-сетки в pygame Surface
"""

import pygame
import config


class Renderer:
    """Класс для рендеринга ASCII-сетки в pygame"""
    
    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.Font(pygame.font.get_default_font(), config.FONT_SIZE)
        # Используем моноширинный шрифт если доступен
        try:
            self.font = pygame.font.Font("consolas.ttf", config.FONT_SIZE)
        except:
            try:
                self.font = pygame.font.Font("courier.ttf", config.FONT_SIZE)
            except:
                pass
        
        # Вычисляем размер окна
        char_width, char_height = self.font.size('M')
        self.char_width = char_width
        self.char_height = char_height
        self.window_width = config.COLS * char_width
        self.window_height = config.ROWS * char_height + 30  # +30 для статусной строки
        
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("ASCII Aquarium")
        
        self.color_mode = 'colored'  # 'monochrome', 'colored', 'night'
    
    def set_color_mode(self, mode):
        """Установить цветовой режим"""
        self.color_mode = mode
    
    def get_color(self, color_name):
        """Получить цвет по имени в зависимости от режима"""
        if self.color_mode == 'monochrome':
            return config.COLOR_MONOCHROME.get(color_name, (255, 255, 255))
        elif self.color_mode == 'night':
            return config.COLOR_NIGHT.get(color_name, (200, 200, 200))
        else:  # colored
            return config.COLOR_COLORED.get(color_name, (255, 255, 255))
    
    def render_grid(self, ascii_grid):
        """
        Отрисовать ASCII-сетку на экран
        """
        self.screen.fill(self.get_color('background'))
        
        # Рендерим каждый символ
        for y in range(ascii_grid.rows):
            for x in range(ascii_grid.cols):
                char = ascii_grid.get_char(x, y)
                if char != ' ':
                    color = ascii_grid.get_color(x, y) or self.get_color('text')
                    text_surface = self.font.render(char, True, color)
                    self.screen.blit(text_surface, (x * self.char_width, y * self.char_height))
    
    def render_frame(self, ascii_grid):
        """Отрисовать рамку вокруг аквариума"""
        color = self.get_color('text')
        # Верхняя и нижняя границы
        for x in range(config.COLS):
            self._draw_char(ascii_grid, x, 0, '-', color)
            self._draw_char(ascii_grid, x, config.ROWS - 1, '-', color)
        # Левая и правая границы
        for y in range(config.ROWS):
            self._draw_char(ascii_grid, 0, y, '|', color)
            self._draw_char(ascii_grid, config.COLS - 1, y, '|', color)
        # Углы
        self._draw_char(ascii_grid, 0, 0, '+', color)
        self._draw_char(ascii_grid, config.COLS - 1, 0, '+', color)
        self._draw_char(ascii_grid, 0, config.ROWS - 1, '+', color)
        self._draw_char(ascii_grid, config.COLS - 1, config.ROWS - 1, '+', color)
    
    def _draw_char(self, grid, x, y, char, color=None):
        """Вспомогательная функция для установки символа"""
        if 0 <= x < config.COLS and 0 <= y < config.ROWS:
            grid.set_char(x, y, char, color)
    
    def render_status_bar(self, ascii_grid, stats):
        """
        Отрисовать статусную строку внизу
        stats - словарь с информацией: {'fish_count', 'food_count', 'current', 'fps', 'mode'}
        """
        y = config.ROWS - 1
        color = self.get_color('text')
        
        # Очищаем строку статуса (предпоследняя)
        status_y = config.ROWS - 2
        for x in range(1, config.COLS - 1):
            ascii_grid.set_char(x, status_y, ' ', None)
        
        # Формируем строку статуса
        fish_count = stats.get('fish_count', 0)
        food_count = stats.get('food_count', 0)
        current_x = stats.get('current_x', 0)
        current_y = stats.get('current_y', 0)
        fps = stats.get('fps', 0)
        mode = stats.get('mode', 'RUNNING')
        
        status_text = f"Fish: {fish_count} | Food: {food_count} | Current: ({current_x:.1f}, {current_y:.1f}) | FPS: {fps:.1f} | {mode}"
        
        # Обрезаем если слишком длинная
        max_len = config.COLS - 2
        if len(status_text) > max_len:
            status_text = status_text[:max_len]
        
        ascii_grid.set_string(1, status_y, status_text, color)
    
    def render_help_overlay(self, ascii_grid):
        """Отрисовать подсказки"""
        help_lines = [
            "Controls:",
            "LMB: Feed | RMB: Delicious feed",
            "A/D or Arrows: Current | W: Change Water",
            "Space: Reset current | +/-: Add/remove fish",
            "N: Night mode | M: Monochrome | R: Randomize",
            "C: Clean | W: Change Water | F: Add Fish",
            "TAB: Care Panel | H: Help | P: Pause",
            "",
            "Press H to hide"
        ]
        
        start_y = config.ROWS // 2 - len(help_lines) // 2
        color = self.get_color('text')
        
        for i, line in enumerate(help_lines):
            y = start_y + i
            if 0 <= y < config.ROWS:
                x = config.COLS // 2 - len(line) // 2
                ascii_grid.set_string(x, y, line, color)
    
    def update(self):
        """Обновить экран"""
        pygame.display.flip()
    
    def pixel_to_grid(self, px, py):
        """Конвертировать пиксельные координаты в координаты сетки"""
        gx = int(px / self.char_width)
        gy = int(py / self.char_height)
        return gx, gy
    
    def grid_to_pixel(self, gx, gy):
        """Конвертировать координаты сетки в пиксельные"""
        px = gx * self.char_width
        py = gy * self.char_height
        return px, py

