"""
Алгоритм boids для поведения стаи
"""

import pygame
import math
import random
import config


def normalize(vec):
    """Нормализовать вектор"""
    if vec.length() < 0.001:
        return pygame.Vector2(0, 0)
    return vec.normalize()


def separation(fish, neighbors):
    """
    Separation: избегание столкновений
    Возвращает силу отталкивания от соседей
    """
    force = pygame.Vector2(0, 0)
    count = 0
    
    for other in neighbors:
        dist = (fish.pos - other.pos).length()
        if 0 < dist < config.R_SEP:
            diff = normalize(fish.pos - other.pos)
            diff /= dist  # Чем ближе, тем сильнее
            force += diff
            count += 1
    
    if count > 0:
        force /= count
        if force.length() > 0:
            force = normalize(force) * fish.max_force
    
    return force


def alignment(fish, neighbors):
    """
    Alignment: выравнивание направления со стаей
    Возвращает силу для изменения направления
    """
    if not neighbors:
        return pygame.Vector2(0, 0)
    
    avg_vel = pygame.Vector2(0, 0)
    count = 0
    
    for other in neighbors:
        dist = (fish.pos - other.pos).length()
        if 0 < dist < config.R_ALIGN:
            avg_vel += other.vel
            count += 1
    
    if count > 0:
        avg_vel /= count
        if avg_vel.length() > 0:
            desired = normalize(avg_vel) * fish.max_speed
            steer = desired - fish.vel
            if steer.length() > fish.max_force:
                steer = normalize(steer) * fish.max_force
            return steer
    
    return pygame.Vector2(0, 0)


def cohesion(fish, neighbors):
    """
    Cohesion: стягивание к центру группы
    Возвращает силу для движения к центру масс соседей
    """
    if not neighbors:
        return pygame.Vector2(0, 0)
    
    center = pygame.Vector2(0, 0)
    count = 0
    
    for other in neighbors:
        dist = (fish.pos - other.pos).length()
        if 0 < dist < config.R_COH:
            center += other.pos
            count += 1
    
    if count > 0:
        center /= count
        return fish.seek(center, fish.max_speed * 0.5)
    
    return pygame.Vector2(0, 0)


def food_attraction(fish, food_list):
    """
    Attraction к корму
    Возвращает силу для движения к ближайшему/самому привлекательному корму
    """
    if not food_list:
        return pygame.Vector2(0, 0)
    
    best_food = None
    best_score = 0
    
    for food in food_list:
        dist = (fish.pos - food.pos).length()
        if dist < food.spread:
            # Оценка привлекательности: amount / dist^2
            score = food.amount / (dist * dist + 1)
            if score > best_score:
                best_score = score
                best_food = food
    
    if best_food:
        # Уменьшаем привлекательность если рыба сытая
        food_weight = config.W_FOOD * (1.0 - fish.energy * 0.5)
        return fish.seek(best_food.pos, fish.max_speed * 0.8) * food_weight
    
    return pygame.Vector2(0, 0)


def apply_boids_forces(fish, neighbors, food_list):
    """
    Применить все силы boids к рыбе с учётом индивидуальности и типа поведения
    """
    # Separation (всегда применяется)
    sep_force = separation(fish, neighbors)
    fish.apply_force(sep_force * config.W_SEP)
    
    # Множители в зависимости от типа поведения
    if fish.behavior_type == 'solitary':
        # Одиночные рыбы - меньше cohesion и alignment
        align_mult = config.SOLITARY_ALIGN_MULT
        coh_mult = config.SOLITARY_COHESION_MULT
        wander_mult = 1.2  # Немного больше wander
    elif fish.behavior_type == 'explorer':
        # Исследователи - больше wander, меньше cohesion
        align_mult = 0.8
        coh_mult = config.EXPLORER_COHESION_MULT
        wander_mult = config.EXPLORER_WANDER_MULT
    else:  # school
        # Стайные - обычное поведение
        align_mult = 1.0
        coh_mult = 1.0
        wander_mult = 1.0
    
    # Alignment и Cohesion зависят от склонности к стае и типа поведения
    school_weight = fish.school_tendency
    
    # Alignment
    align_force = alignment(fish, neighbors)
    fish.apply_force(align_force * config.W_ALIGN * school_weight * align_mult)
    
    # Cohesion
    coh_force = cohesion(fish, neighbors)
    fish.apply_force(coh_force * config.W_COH * school_weight * coh_mult)
    
    # Food attraction (зависит от любопытства и энергии)
    food_force = food_attraction(fish, food_list)
    curiosity_multiplier = 0.5 + fish.curiosity * 0.5
    fish.apply_force(food_force * curiosity_multiplier)
    
    # Периодические случайные "толчки" для хаотичности (больше для исследователей)
    chaos_chance = 0.01 * fish.chaos_factor
    if fish.behavior_type == 'explorer':
        chaos_chance *= 1.5
    if random.random() < chaos_chance:
        random_force = pygame.Vector2(
            random.uniform(-1, 1),
            random.uniform(-1, 1)
        ) * fish.max_force * 0.3 * fish.chaos_factor
        fish.apply_force(random_force)

