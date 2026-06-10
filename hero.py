import os

import arcade

from items import RARITY_COMMON, Item
from settings import (HERO_ATTACK, HERO_DEFENSE, HERO_START_GOLD,
                      HERO_START_HP, LEVEL_UP_HP_BONUS, LEVEL_UP_STAT_BONUS,
                      TILE_SIZE, UPGRADE_AMOUNT, UPGRADE_ATTACK_COST,
                      UPGRADE_DEFENSE_COST, UPGRADE_HP_COST, XP_TO_LEVEL_UP, MAX_ATTACK, MAX_DEFENSE, MAX_HP)


class Hero:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.gold = HERO_START_GOLD
        self.hp = HERO_START_HP
        self.max_hp = HERO_START_HP
        self.attack = HERO_ATTACK
        self.defense = HERO_DEFENSE
        
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = XP_TO_LEVEL_UP
                # Инвентарь и экипировка
        self.inventory = []  # Список предметов
        self.max_inventory = 20
        
        # Слоты экипировки
        self.equipped_weapon = None
        self.equipped_armor = None
        self.equipped_accessory = None
        
        # Бонусы от экипировки
        self.bonus_attack = 0
        self.bonus_defense = 0
        self.bonus_hp = 0
        # Загрузка текстуры героя
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, "images", "hero.png")
        try:
            self.texture = arcade.load_texture(image_path)
        except FileNotFoundError:
            print(f"⚠️  Файл hero.png не найден! Использую эмодзи.")
            self.texture = None
    
    def draw(self, screen_x, screen_y):
        # Полоска здоровья
        hp_ratio = self.hp / self.max_hp
        bar_width = int(TILE_SIZE * hp_ratio)
        bar_x = screen_x
        bar_y = screen_y + TILE_SIZE + 5
        
        arcade.draw_lbwh_rectangle_filled(bar_x, bar_y, TILE_SIZE, 5, (100, 100, 100))
        if bar_width > 0:
            arcade.draw_lbwh_rectangle_filled(bar_x, bar_y, bar_width, 5, (30, 144, 255))
        
        # Рисуем героя (картинку или эмодзи)
        if self.texture:
            # Масштабируем картинку под размер клетки
            scale = TILE_SIZE / max(self.texture.width, self.texture.height)
            center_x = screen_x + TILE_SIZE // 2
            center_y = screen_y + TILE_SIZE // 2
            
            # Создаём прямоугольник через arcade.XYWH (Arcade 3.x)
            rect = arcade.XYWH(
                center_x,
                center_y,
                self.texture.width * scale,
                self.texture.height * scale
            )
            arcade.draw_texture_rect(self.texture, rect)
        else:
            # Рисуем эмодзи если картинка не найдена
            arcade.draw_text(
                "🤴",
                screen_x + TILE_SIZE // 2,
                screen_y + TILE_SIZE // 2,
                arcade.color.WHITE,
                44,
                anchor_x="center",
                anchor_y="center",
                font_name="Segoe UI Emoji"
            )
        
        # Уровень
        arcade.draw_text(
            f"Lv.{self.level}",
            screen_x + TILE_SIZE - 6,
            screen_y + 6,
            (255, 255, 0),
            11,
            anchor_x="right",
            anchor_y="bottom",
            font_name="Arial",
            bold=True
        )
    
    def take_damage(self, damage):
        """Расчёт урона с учётом защиты (каждая ед. защиты = 0.6 урона)"""
        damage_reduction = self.defense * 0.6
        actual_damage = max(1, damage - damage_reduction)
        actual_damage = int(actual_damage)
        self.hp -= actual_damage
        return actual_damage
    
    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)
    
    def is_alive(self):
        return self.hp > 0
    
    def gain_xp(self, amount):
        self.xp += amount
        leveled_up = False
        
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level += 1
            self.max_hp += LEVEL_UP_HP_BONUS
            self.hp = self.max_hp
            self.attack += LEVEL_UP_STAT_BONUS
            self.defense += LEVEL_UP_STAT_BONUS
            self.xp_to_next_level = int(self.xp_to_next_level * 1.5)
            leveled_up = True
            
        return leveled_up


    def upgrade_attack(self):
        """Улучшение атаки (мягкий рост стоимости)"""
        if self.attack >= MAX_ATTACK:
            return False
        
        current_level = self.attack - HERO_ATTACK
        cost = int(UPGRADE_ATTACK_COST * (1.5 ** current_level))  # 200, 300, 450, 675...
        
        if self.gold >= cost:
            self.gold -= cost
            self.attack += UPGRADE_AMOUNT
            return True
        return False
    
    def upgrade_defense(self):
        """Улучшение защиты (мягкий рост стоимости)"""
        if self.defense >= MAX_DEFENSE:
            return False
        
        current_level = self.defense - HERO_DEFENSE
        cost = int(UPGRADE_DEFENSE_COST * (1.5 ** current_level))  # 200, 300, 450, 675...
        
        if self.gold >= cost:
            self.gold -= cost
            self.defense += UPGRADE_AMOUNT
            return True
        return False
    
    def upgrade_hp(self):
        """Улучшение HP (мягкий рост стоимости)"""
        if self.max_hp >= MAX_HP:
            return False
        
        current_level = (self.max_hp - HERO_START_HP) // (UPGRADE_AMOUNT * 2)
        cost = int(UPGRADE_HP_COST * (1.5 ** current_level))  # 300, 450, 675, 1012...
        
        if self.gold >= cost:
            self.gold -= cost
            hp_increase = UPGRADE_AMOUNT * 2
            self.max_hp += hp_increase
            self.hp += hp_increase
            return True
        return False
    

    def add_to_inventory(self, item):
        """Добавляет предмет в инвентарь"""
        if len(self.inventory) >= self.max_inventory:
            return False, "Инвентарь полон!"
        
        self.inventory.append(item)
        return True, f"Получен предмет: {item.name}"
    
    def remove_from_inventory(self, index):
        """Удаляет предмет из инвентаря по индексу"""
        if 0 <= index < len(self.inventory):
            return self.inventory.pop(index)
        return None
    
    def equip_item(self, index):
        """Экипирует предмет по индексу"""
        if index < 0 or index >= len(self.inventory):
            return False, "Неверный индекс"
        
        item = self.inventory[index]
        
        if item.type == "weapon":
            # Снимаем текущее оружие
            if self.equipped_weapon:
                self.inventory.append(self.equipped_weapon)
            self.equipped_weapon = item
        elif item.type == "armor":
            if self.equipped_armor:
                self.inventory.append(self.equipped_armor)
            self.equipped_armor = item
        elif item.type == "accessory":
            if self.equipped_accessory:
                self.inventory.append(self.equipped_accessory)
            self.equipped_accessory = item
        else:
            return False, "Этот предмет нельзя экипировать"
        
        # Удаляем из инвентаря
        self.inventory.pop(index)
        
        # Пересчитываем бонусы
        self.recalculate_bonuses()
        
        return True, f"Экипировано: {item.name}"
    
    def unequip_item(self, slot):
        """Снимает предмет из слота"""
        if slot == "weapon":
            item = self.equipped_weapon
            self.equipped_weapon = None
        elif slot == "armor":
            item = self.equipped_armor
            self.equipped_armor = None
        elif slot == "accessory":
            item = self.equipped_accessory
            self.equipped_accessory = None
        else:
            return False, "Неверный слот"
        
        if item:
            if len(self.inventory) < self.max_inventory:
                self.inventory.append(item)
                self.recalculate_bonuses()
                return True, f"Снято: {item.name}"
            else:
                # Инвентарь полон, предмет выпадает
                return True, f"Снято: {item.name} (инвентарь полон!)"
        
        return False, "Слот пуст"
    
    def recalculate_bonuses(self):
        """Пересчитывает бонусы от экипировки"""
        self.bonus_attack = 0
        self.bonus_defense = 0
        self.bonus_hp = 0
        
        for item in [self.equipped_weapon, self.equipped_armor, self.equipped_accessory]:
            if item:
                self.bonus_attack += item.attack
                self.bonus_defense += item.defense
                self.bonus_hp += item.hp
        
        # Обновляем максимальное HP
        base_max_hp = 120 + (self.level - 1) * 25  # Базовое HP + за уровни
        self.max_hp = base_max_hp + self.bonus_hp
        
        # Если текущее HP больше нового максимума, обрезаем
        if self.hp > self.max_hp:
            self.hp = self.max_hp
    
    def get_total_attack(self):
        """Возвращает общую атаку (база + бонусы)"""
        return self.attack + self.bonus_attack
    
    def get_total_defense(self):
        """Возвращает общую защиту (база + бонусы)"""
        return self.defense + self.bonus_defense