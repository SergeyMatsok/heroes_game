import arcade
import os
from settings import (
    TILE_SIZE, HERO_START_GOLD, HERO_START_HP,
    HERO_ATTACK, HERO_DEFENSE,
    UPGRADE_ATTACK_COST, UPGRADE_DEFENSE_COST, UPGRADE_HP_COST, UPGRADE_AMOUNT,
    XP_TO_LEVEL_UP, LEVEL_UP_HP_BONUS, LEVEL_UP_STAT_BONUS
)

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
        actual_damage = max(1, damage - self.defense)
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
        if self.gold >= UPGRADE_ATTACK_COST:
            self.gold -= UPGRADE_ATTACK_COST
            self.attack += UPGRADE_AMOUNT
            return True
        return False
    
    def upgrade_defense(self):
        if self.gold >= UPGRADE_DEFENSE_COST:
            self.gold -= UPGRADE_DEFENSE_COST
            self.defense += UPGRADE_AMOUNT
            return True
        return False
    
    def upgrade_hp(self):
        if self.gold >= UPGRADE_HP_COST:
            self.gold -= UPGRADE_HP_COST
            self.max_hp += UPGRADE_AMOUNT * 2
            self.hp += UPGRADE_AMOUNT * 2
            return True
        return False