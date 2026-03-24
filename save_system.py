"""
Система сохранения и загрузки состояния аквариума
"""

import json
import os
import pygame
import config
from sim.fish import Fish
from sim.food import FoodPellet


def save_aquarium_state(app, filepath=None):
    """Сохранить состояние аквариума"""
    if filepath is None:
        filepath = config.SAVE_FILE
    
    try:
        state = {
            'world': {
                'time': app.world.time,
                'current_x': app.world.current.x,
                'current_y': app.world.current.y,
                'light_level': app.world.light_level,
                'water_quality': {
                    'pollution': app.world.water_quality.pollution,
                    'oxygen': app.world.water_quality.oxygen,
                    'temperature': app.world.water_quality.temperature,
                }
            },
            'fish': [],
            'food': [],
            'last_fed_time': app.last_fed_time,
        }
        
        # Сохраняем рыб
        for fish in app.fish_list:
            fish_data = {
                'pos_x': fish.pos.x,
                'pos_y': fish.pos.y,
                'vel_x': fish.vel.x,
                'vel_y': fish.vel.y,
                'size': fish.size,
                'energy': fish.energy,
                'health': fish.health,
                'age': fish.age,
                'behavior_type': fish.behavior_type,
                'chaos_factor': fish.chaos_factor,
                'curiosity': fish.curiosity,
                'school_tendency': fish.school_tendency,
                'color_variant': fish.color_variant,
                'color_hue_shift': fish.color_hue_shift,
                'color_saturation': fish.color_saturation,
                'max_speed': fish.max_speed,
                'max_force': fish.max_force,
            }
            state['fish'].append(fish_data)
        
        # Сохраняем корм
        for food in app.food_list:
            food_data = {
                'pos_x': food.pos.x,
                'pos_y': food.pos.y,
                'amount': food.amount,
                'ttl': food.ttl,
                'char': food.char,
            }
            state['food'].append(food_data)
        
        # Записываем в файл
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Ошибка сохранения: {e}")
        return False


def load_aquarium_state(app, filepath=None):
    """Загрузить состояние аквариума"""
    if filepath is None:
        filepath = config.SAVE_FILE
    
    if not os.path.exists(filepath):
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        # Восстанавливаем мир
        app.world.time = state['world']['time']
        app.world.current = pygame.Vector2(
            state['world']['current_x'],
            state['world']['current_y']
        )
        app.world.light_level = state['world']['light_level']
        
        # Восстанавливаем качество воды
        wq = state['world']['water_quality']
        app.world.water_quality.pollution = wq['pollution']
        app.world.water_quality.oxygen = wq['oxygen']
        app.world.water_quality.temperature = wq.get('temperature', 22.0)
        
        # Восстанавливаем рыб
        app.fish_list = []
        for fish_data in state['fish']:
            pos = pygame.Vector2(fish_data['pos_x'], fish_data['pos_y'])
            fish = Fish(pos, app.world)
            
            fish.vel = pygame.Vector2(fish_data['vel_x'], fish_data['vel_y'])
            fish.size = fish_data['size']
            fish.energy = fish_data['energy']
            fish.health = fish_data['health']
            fish.age = fish_data['age']
            fish.behavior_type = fish_data.get('behavior_type', 'school')
            fish.chaos_factor = fish_data.get('chaos_factor', 1.0)
            fish.curiosity = fish_data.get('curiosity', 0.7)
            fish.school_tendency = fish_data.get('school_tendency', 1.0)
            fish.color_variant = fish_data.get('color_variant', 1.0)
            fish.color_hue_shift = fish_data.get('color_hue_shift', 0.0)
            fish.color_saturation = fish_data.get('color_saturation', 0.8)
            fish.max_speed = fish_data.get('max_speed', fish.max_speed)
            fish.max_force = fish_data.get('max_force', fish.max_force)
            fish.is_alive = fish.health > config.FISH_MIN_HEALTH_TO_LIVE
            
            app.fish_list.append(fish)
        
        # Восстанавливаем корм
        app.food_list = []
        for food_data in state['food']:
            pos = pygame.Vector2(food_data['pos_x'], food_data['pos_y'])
            food = FoodPellet(pos, app.world, delicious=(food_data['char'] == config.SYMBOLS['food_delicious']))
            food.amount = food_data['amount']
            food.ttl = food_data['ttl']
            app.food_list.append(food)
        
        # Восстанавливаем время последнего кормления
        app.last_fed_time = state.get('last_fed_time', 0.0)
        
        return True
    except Exception as e:
        print(f"Ошибка загрузки: {e}")
        return False

