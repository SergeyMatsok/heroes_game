import arcade
from settings import (
    TILE_SIZE,
    ENEMY_WOLF_HP, ENEMY_WOLF_ATTACK, ENEMY_WOLF_DEFENSE,
    ENEMY_GOBLIN_HP, ENEMY_GOBLIN_ATTACK, ENEMY_GOBLIN_DEFENSE,
    ENEMY_SKELETON_HP, ENEMY_SKELETON_ATTACK, ENEMY_SKELETON_DEFENSE,
    ENEMY_LICH_HP, ENEMY_LICH_ATTACK, ENEMY_LICH_DEFENSE,
    ENEMY_GOLEM_HP, ENEMY_GOLEM_ATTACK, ENEMY_GOLEM_DEFENSE,
    ENEMY_DRAGON_HP, ENEMY_DRAGON_ATTACK, ENEMY_DRAGON_DEFENSE,
    ENEMY_SCALING_PER_WEEK
)

class Enemy:
    def __init__(self, x, y, enemy_type="goblin", spawn_week=1):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.spawn_week = spawn_week
        self.is_aggroed = False
        
        if enemy_type == "dragon":
            self.base_hp, self.base_attack, self.base_defense = ENEMY_DRAGON_HP, ENEMY_DRAGON_ATTACK, ENEMY_DRAGON_DEFENSE
            self.emoji = "🐉"
        elif enemy_type == "golem":
            self.base_hp, self.base_attack, self.base_defense = ENEMY_GOLEM_HP, ENEMY_GOLEM_ATTACK, ENEMY_GOLEM_DEFENSE
            self.emoji = "🗿"
        elif enemy_type == "lich":
            self.base_hp, self.base_attack, self.base_defense = ENEMY_LICH_HP, ENEMY_LICH_ATTACK, ENEMY_LICH_DEFENSE
            self.emoji = "🧙‍♂️"
        elif enemy_type == "skeleton":
            self.base_hp, self.base_attack, self.base_defense = ENEMY_SKELETON_HP, ENEMY_SKELETON_ATTACK, ENEMY_SKELETON_DEFENSE
            self.emoji = "💀"
        elif enemy_type == "wolf":
            self.base_hp, self.base_attack, self.base_defense = ENEMY_WOLF_HP, ENEMY_WOLF_ATTACK, ENEMY_WOLF_DEFENSE
            self.emoji = "🐺"
        else:  # goblin
            self.base_hp, self.base_attack, self.base_defense = ENEMY_GOBLIN_HP, ENEMY_GOBLIN_ATTACK, ENEMY_GOBLIN_DEFENSE
            self.emoji = "👺"
            
        self.update_stats()

    def update_stats(self):
        multiplier = 1.0 + (self.spawn_week - 1) * ENEMY_SCALING_PER_WEEK
        hp_ratio = self.hp / self.max_hp if hasattr(self, 'max_hp') and self.max_hp > 0 else 1.0
        
        self.max_hp = int(self.base_hp * multiplier)
        self.hp = int(self.max_hp * hp_ratio)
        self.attack = int(self.base_attack * multiplier)
        self.defense = int(self.base_defense * multiplier)
        
        if self.spawn_week == 1:
            self.title = ""
        elif self.spawn_week <= 3:
            self.title = " (Опытный)"
        else:
            self.title = " (Элитный)"

    def draw(self, screen_x, screen_y):
        hp_ratio = self.hp / self.max_hp
        bar_width = int(TILE_SIZE * hp_ratio)
        bar_x = screen_x
        bar_y = screen_y + TILE_SIZE + 5
        
        arcade.draw_lbwh_rectangle_filled(bar_x, bar_y, TILE_SIZE, 5, (100, 100, 100))
        if bar_width > 0:
            arcade.draw_lbwh_rectangle_filled(bar_x, bar_y, bar_width, 5, (220, 20, 60))
        
        shadow_color = (255, 0, 0, 150) if self.is_aggroed else (0, 0, 0, 100)
        
        arcade.draw_text(
            self.emoji, screen_x + TILE_SIZE // 2 + 2, screen_y + TILE_SIZE // 2 - 2,
            shadow_color, 42, anchor_x="center", anchor_y="center", font_name="Segoe UI Emoji"
        )
        arcade.draw_text(
            self.emoji, screen_x + TILE_SIZE // 2, screen_y + TILE_SIZE // 2,
            arcade.color.WHITE, 42, anchor_x="center", anchor_y="center", font_name="Segoe UI Emoji"
        )
    
    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense)
        self.hp -= actual_damage
        return actual_damage
    
    def is_alive(self):
        return self.hp > 0