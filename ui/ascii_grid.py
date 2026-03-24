"""
Буфер ASCII-символов для рендеринга
"""

import config


class AsciiGrid:
    """Буфер для хранения ASCII-символов и их цветов"""
    
    def __init__(self):
        self.cols = config.COLS
        self.rows = config.ROWS
        self.clear()
    
    def clear(self):
        """Очистить сетку (заполнить пробелами)"""
        self.grid = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]
        self.colors = [[None for _ in range(self.cols)] for _ in range(self.rows)]
    
    def set_char(self, x, y, char, color=None):
        """
        Установить символ в позиции (x, y)
        x, y - координаты в сетке (0..cols-1, 0..rows-1)
        """
        if 0 <= x < self.cols and 0 <= y < self.rows:
            self.grid[y][x] = char
            if color is not None:
                self.colors[y][x] = color
    
    def set_string(self, x, y, string, color=None):
        """
        Установить строку начиная с позиции (x, y)
        """
        for i, char in enumerate(string):
            self.set_char(x + i, y, char, color)
    
    def get_char(self, x, y):
        """Получить символ в позиции"""
        if 0 <= x < self.cols and 0 <= y < self.rows:
            return self.grid[y][x]
        return ' '
    
    def get_color(self, x, y):
        """Получить цвет в позиции"""
        if 0 <= x < self.cols and 0 <= y < self.rows:
            return self.colors[y][x]
        return None

