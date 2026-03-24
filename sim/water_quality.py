"""
Система качества воды в аквариуме
"""

import config


class WaterQuality:
    """Класс для управления качеством воды"""
    
    def __init__(self):
        self.pollution = 0.0  # Загрязнение (0.0 - 1.0)
        self.oxygen = 1.0  # Уровень кислорода (0.0 - 1.0)
        self.temperature = 22.0  # Температура (опционально, в градусах)
    
    def update(self, dt, fish_count):
        """Обновить качество воды"""
        # Рост загрязнения (базовый + от рыб)
        pollution_gain = (config.WATER_POLLUTION_RATE + 
                         fish_count * config.WATER_POLLUTION_PER_FISH) * dt
        self.pollution = min(1.0, self.pollution + pollution_gain)
        
        # Кислород уменьшается при загрязнении
        oxygen_loss = config.WATER_OXYGEN_DECAY * self.pollution * dt
        self.oxygen = max(0.0, self.oxygen - oxygen_loss)
        
        # Кислород немного восстанавливается естественным путём
        if self.pollution < 0.5:
            self.oxygen = min(1.0, self.oxygen + dt * 0.0001)
    
    def clean(self):
        """Очистка аквариума"""
        self.pollution = max(0.0, self.pollution - config.WATER_CLEAN_AMOUNT)
        # Очистка немного улучшает кислород
        self.oxygen = min(1.0, self.oxygen + 0.1)
    
    def change_water(self):
        """Смена воды"""
        self.pollution = 0.0
        self.oxygen = 1.0
    
    def get_quality(self):
        """Получить общее качество воды (0.0 - 1.0)"""
        # Среднее между чистотой и кислородом
        return (1.0 - self.pollution + self.oxygen) / 2.0
    
    def get_status(self):
        """Получить текстовый статус качества воды"""
        quality = self.get_quality()
        if quality > 0.7:
            return "EXCELLENT"
        elif quality > 0.5:
            return "GOOD"
        elif quality > 0.3:
            return "POOR"
        else:
            return "CRITICAL"

