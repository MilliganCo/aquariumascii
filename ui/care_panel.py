"""
Панель ухода за аквариумом
"""

import config


class CarePanel:
    """Класс для отображения панели ухода"""
    
    @staticmethod
    def render_to_grid(grid, world, fish_list, last_fed_time):
        """Отрисовать панель ухода в сетку"""
        # Вычисляем среднее здоровье рыб
        if fish_list:
            avg_health = sum(f.health for f in fish_list) / len(fish_list)
        else:
            avg_health = 0.0
        
        # Качество воды
        water_quality = world.water_quality.get_quality()
        pollution = world.water_quality.pollution
        
        # Время с последнего кормления
        time_since_fed = world.time - last_fed_time
        
        # Позиция панели (справа вверху)
        start_x = config.COLS - 35
        start_y = 1
        
        # Рамка панели
        panel_width = 33
        panel_height = 12
        
        # Верхняя и нижняя границы
        for x in range(start_x, start_x + panel_width):
            if x < config.COLS:
                grid.set_char(x, start_y, '-', None)
                grid.set_char(x, start_y + panel_height - 1, '-', None)
        
        # Левая и правая границы
        for y in range(start_y, start_y + panel_height):
            if y < config.ROWS:
                grid.set_char(start_x, y, '|', None)
                grid.set_char(start_x + panel_width - 1, y, '|', None)
        
        # Углы
        grid.set_char(start_x, start_y, '+', None)
        grid.set_char(start_x + panel_width - 1, start_y, '+', None)
        grid.set_char(start_x, start_y + panel_height - 1, '+', None)
        grid.set_char(start_x + panel_width - 1, start_y + panel_height - 1, '+', None)
        
        # Заголовок
        title = "Care Panel"
        title_x = start_x + (panel_width - len(title)) // 2
        grid.set_string(title_x, start_y + 1, title, None)
        
        # Разделитель
        for x in range(start_x + 1, start_x + panel_width - 1):
            grid.set_char(x, start_y + 2, '-', None)
        
        # Здоровье рыб
        health_bar = CarePanel._create_bar(avg_health, 20)
        health_text = f"Health: {health_bar} {int(avg_health * 100)}%"
        grid.set_string(start_x + 1, start_y + 3, health_text[:panel_width - 2], None)
        
        # Качество воды
        quality_bar = CarePanel._create_bar(water_quality, 20)
        quality_text = f"Water: {quality_bar} {int(water_quality * 100)}%"
        grid.set_string(start_x + 1, start_y + 4, quality_text[:panel_width - 2], None)
        
        # Загрязнение
        pollution_bar = CarePanel._create_bar(pollution, 20)
        pollution_status = "HIGH" if pollution > 0.7 else "OK" if pollution < 0.4 else "MED"
        pollution_text = f"Pollution: {pollution_bar} {pollution_status}"
        grid.set_string(start_x + 1, start_y + 5, pollution_text[:panel_width - 2], None)
        
        # Время с последнего кормления
        minutes = int(time_since_fed // 60)
        seconds = int(time_since_fed % 60)
        fed_text = f"Last Fed: {minutes}m {seconds}s"
        grid.set_string(start_x + 1, start_y + 6, fed_text[:panel_width - 2], None)
        
        # Количество рыб
        fish_text = f"Fish: {len(fish_list)}"
        grid.set_string(start_x + 1, start_y + 7, fish_text[:panel_width - 2], None)
        
        # Управление
        grid.set_string(start_x + 1, start_y + 9, "[C] Clean [W] Water", None)
        grid.set_string(start_x + 1, start_y + 10, "[F] Add Fish [TAB] Toggle", None)
    
    @staticmethod
    def _create_bar(value, length):
        """Создать текстовую полосу прогресса"""
        filled = int(value * length)
        bar = '█' * filled + '░' * (length - filled)
        return bar

