"""
Spatial hash grid для оптимизации поиска соседей
"""

import config


class SpatialHash:
    """Класс для пространственного хеширования"""
    
    def __init__(self, world_width, world_height):
        self.world_width = world_width
        self.world_height = world_height
        self.cell_size = config.SPATIAL_HASH_CELL_SIZE
        self.cols = int(world_width / self.cell_size) + 1
        self.rows = int(world_height / self.cell_size) + 1
        self.grid = [[[] for _ in range(self.cols)] for _ in range(self.rows)]
    
    def clear(self):
        """Очистить сетку"""
        self.grid = [[[] for _ in range(self.cols)] for _ in range(self.rows)]
    
    def _get_cell(self, x, y):
        """Получить индексы ячейки для координат"""
        cx = int(x / self.cell_size)
        cy = int(y / self.cell_size)
        cx = max(0, min(cx, self.cols - 1))
        cy = max(0, min(cy, self.rows - 1))
        return cx, cy
    
    def insert(self, obj, pos):
        """Добавить объект в сетку"""
        cx, cy = self._get_cell(pos.x, pos.y)
        self.grid[cy][cx].append(obj)
    
    def get_neighbors(self, pos, radius=None):
        """
        Получить соседей в радиусе
        Проверяет текущую ячейку и 8 соседних
        """
        cx, cy = self._get_cell(pos.x, pos.y)
        neighbors = []
        
        # Проверяем текущую ячейку и соседние
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx = cx + dx
                ny = cy + dy
                if 0 <= nx < self.cols and 0 <= ny < self.rows:
                    neighbors.extend(self.grid[ny][nx])
        
        # Если указан радиус, фильтруем по расстоянию
        if radius is not None:
            filtered = []
            for neighbor in neighbors:
                dist = (pos - neighbor.pos).length()
                if dist <= radius:
                    filtered.append(neighbor)
            return filtered
        
        return neighbors

