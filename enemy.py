import arcade
import os
from settings import (
    TILE_SIZE,
    ENEMY_WOLF_HP, ENEMY_WOLF_ATTACK, ENEMY_WOLF_DEFENSE,
    ENEMY_GOBLIN_HP, ENEMY_GOBLIN_ATTACK, ENEMY_GOBLIN_DEFENSE,
    ENEMY_SKELETON_HP, ENEMY_SKELETON_ATTACK, ENEMY_SKELETON_DEFENSE,
    ENEMY_LICH_HP, ENEMY_LICH_ATTACK, ENEMY_LICH_DEFENSE,
    ENEMY_GOLEM_HP, ENEMY_GOLEM_ATTACK, ENEMY_GOLEM_DEFENSE,
    ENEMY_DRAGON_HP, ENEMY_DRAGON_ATTACK, ENEMY_DRAGON_DEFENSE,
    ENEMY_ORC_HP, ENEMY_ORC_ATTACK, ENEMY_ORC_DEFENSE,
    ENEMY_TROLL_HP, ENEMY_TROLL_ATTACK, ENEMY_TROLL_DEFENSE,
    ENEMY_VAMPIRE_HP, ENEMY_VAMPIRE_ATTACK, ENEMY_VAMPIRE_DEFENSE,
    ENEMY_DEMON_HP, ENEMY_DEMON_ATTACK, ENEMY_DEMON_DEFENSE,
    ENEMY_BANDIT_HP, ENEMY_BANDIT_ATTACK, ENEMY_BANDIT_DEFENSE,
    ENEMY_DARK_ELF_HP, ENEMY_DARK_ELF_ATTACK, ENEMY_DARK_ELF_DEFENSE,
    ENEMY_GIANT_HP, ENEMY_GIANT_ATTACK, ENEMY_GIANT_DEFENSE,
    ENEMY_PHOENIX_HP, ENEMY_PHOENIX_ATTACK, ENEMY_PHOENIX_DEFENSE,
    ENEMY_SCALING_PER_WEEK
)

# Словарь с эмодзи (fallback если картинки не найдены)
ENEMY_EMOJIS = {
    "wolf": "🐺",
    "goblin": "👺",
    "skeleton": "💀",
    "lich": "🧙",
    "golem": "🗿",
    "dragon": "🐉",
    "orc": "👹",
    "troll": "🧌",
    "vampire": "🧛",
    "demon": "😈",
    "bandit": "🥷",
    "dark_elf": "🧝",
    "giant": "🧟",
    "phoenix": "🦅"
}

# Кэш текстур (чтобы не загружать одну и ту же картинку много раз)
TEXTURE_CACHE = {}

def load_enemy_texture(enemy_type):
    """Загружает текстуру врага (с кэшированием)"""
    if enemy_type in TEXTURE_CACHE:
        return TEXTURE_CACHE[enemy_type]
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, "images", f"{enemy_type}.png")
    
    try:
        texture = arcade.load_texture(image_path)
        TEXTURE_CACHE[enemy_type] = texture
        return texture
    except FileNotFoundError:
        print(f"⚠️  Файл {enemy_type}.png не найден! Использую эмодзи.")
        TEXTURE_CACHE[enemy_type] = None
        return None


class Enemy:
    def __init__(self, x, y, enemy_type="goblin", spawn_week=1):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.spawn_week = spawn_week
        self.is_aggroed = False
        
        # Загружаем текстуру
        self.texture = load_enemy_texture(enemy_type)
        
        # Базовые характеристики в зависимости от типа врага
        if enemy_type == "wolf":
            self.base_hp = ENEMY_WOLF_HP
            self.base_attack = ENEMY_WOLF_ATTACK
            self.base_defense = ENEMY_WOLF_DEFENSE
        elif enemy_type == "goblin":
            self.base_hp = ENEMY_GOBLIN_HP
            self.base_attack = ENEMY_GOBLIN_ATTACK
            self.base_defense = ENEMY_GOBLIN_DEFENSE
        elif enemy_type == "skeleton":
            self.base_hp = ENEMY_SKELETON_HP
            self.base_attack = ENEMY_SKELETON_ATTACK
            self.base_defense = ENEMY_SKELETON_DEFENSE
        elif enemy_type == "lich":
            self.base_hp = ENEMY_LICH_HP
            self.base_attack = ENEMY_LICH_ATTACK
            self.base_defense = ENEMY_LICH_DEFENSE
        elif enemy_type == "golem":
            self.base_hp = ENEMY_GOLEM_HP
            self.base_attack = ENEMY_GOLEM_ATTACK
            self.base_defense = ENEMY_GOLEM_DEFENSE
        elif enemy_type == "dragon":
            self.base_hp = ENEMY_DRAGON_HP
            self.base_attack = ENEMY_DRAGON_ATTACK
            self.base_defense = ENEMY_DRAGON_DEFENSE
        elif enemy_type == "orc":
            self.base_hp = ENEMY_ORC_HP
            self.base_attack = ENEMY_ORC_ATTACK
            self.base_defense = ENEMY_ORC_DEFENSE
        elif enemy_type == "troll":
            self.base_hp = ENEMY_TROLL_HP
            self.base_attack = ENEMY_TROLL_ATTACK
            self.base_defense = ENEMY_TROLL_DEFENSE
        elif enemy_type == "vampire":
            self.base_hp = ENEMY_VAMPIRE_HP
            self.base_attack = ENEMY_VAMPIRE_ATTACK
            self.base_defense = ENEMY_VAMPIRE_DEFENSE
        elif enemy_type == "demon":
            self.base_hp = ENEMY_DEMON_HP
            self.base_attack = ENEMY_DEMON_ATTACK
            self.base_defense = ENEMY_DEMON_DEFENSE
        elif enemy_type == "bandit":
            self.base_hp = ENEMY_BANDIT_HP
            self.base_attack = ENEMY_BANDIT_ATTACK
            self.base_defense = ENEMY_BANDIT_DEFENSE
        elif enemy_type == "dark_elf":
            self.base_hp = ENEMY_DARK_ELF_HP
            self.base_attack = ENEMY_DARK_ELF_ATTACK
            self.base_defense = ENEMY_DARK_ELF_DEFENSE
        elif enemy_type == "giant":
            self.base_hp = ENEMY_GIANT_HP
            self.base_attack = ENEMY_GIANT_ATTACK
            self.base_defense = ENEMY_GIANT_DEFENSE
        elif enemy_type == "phoenix":
            self.base_hp = ENEMY_PHOENIX_HP
            self.base_attack = ENEMY_PHOENIX_ATTACK
            self.base_defense = ENEMY_PHOENIX_DEFENSE
        else:
            # По умолчанию — гоблин
            self.base_hp = ENEMY_GOBLIN_HP
            self.base_attack = ENEMY_GOBLIN_ATTACK
            self.base_defense = ENEMY_GOBLIN_DEFENSE
        
        # Эмодзи для отрисовки
        self.emoji = ENEMY_EMOJIS.get(enemy_type, "❓")
        
        self.update_stats()

    def update_stats(self):
        """Пересчитывает характеристики в зависимости от текущей недели"""
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
        # Полоска здоровья
        hp_ratio = self.hp / self.max_hp
        bar_width = int(TILE_SIZE * hp_ratio)
        bar_x = screen_x
        bar_y = screen_y + TILE_SIZE + 5
        
        arcade.draw_lbwh_rectangle_filled(bar_x, bar_y, TILE_SIZE, 5, (100, 100, 100))
        if bar_width > 0:
            arcade.draw_lbwh_rectangle_filled(bar_x, bar_y, bar_width, 5, (220, 20, 60))
        
        center_x = screen_x + TILE_SIZE // 2
        center_y = screen_y + TILE_SIZE // 2
        
        # Рисуем моба (картинку или эмодзи)
        if self.texture:
            # Масштабируем картинку под размер клетки
            scale = TILE_SIZE / max(self.texture.width, self.texture.height)
            rect = arcade.XYWH(
                center_x,
                center_y,
                self.texture.width * scale,
                self.texture.height * scale
            )
            arcade.draw_texture_rect(self.texture, rect)
        else:
            # Fallback на эмодзи
            shadow_color = (255, 0, 0, 150) if self.is_aggroed else (0, 0, 0, 100)
            
            arcade.draw_text(
                self.emoji,
                center_x + 2,
                center_y - 2,
                shadow_color,
                42,
                anchor_x="center",
                anchor_y="center",
                font_name="Segoe UI Emoji"
            )
            arcade.draw_text(
                self.emoji,
                center_x,
                center_y,
                arcade.color.WHITE,
                42,
                anchor_x="center",
                anchor_y="center",
                font_name="Segoe UI Emoji"
            )
        
        # 🔥 УРОВЕНЬ ВРАГА (в правом нижнем углу)
        enemy_level = self.spawn_week
        arcade.draw_text(
            f"Lv.{enemy_level}",
            screen_x + TILE_SIZE - 4,
            screen_y + 4,
            (255, 255, 0),  # Жёлтый цвет
            12,
            anchor_x="right",
            anchor_y="bottom",
            font_name="Arial",
            bold=True
        )
        
        # Название типа врага (сверху)
        enemy_names = {
            "wolf": "Волк",
            "goblin": "Гоблин",
            "skeleton": "Скелет",
            "lich": "Лич",
            "golem": "Голем",
            "dragon": "Дракон",
            "orc": "Орк",
            "troll": "Тролль",
            "vampire": "Вампир",
            "demon": "Демон",
            "bandit": "Бандит",
            "dark_elf": "Тёмный эльф",
            "giant": "Великан",
            "phoenix": "Феникс"
        }
        name = enemy_names.get(self.type, self.type)
        if self.title:
            name += self.title
        
        arcade.draw_text(
            name,
            screen_x + TILE_SIZE // 2,
            screen_y + TILE_SIZE + 15,
            (255, 200, 100),  # Оранжевый
            10,
            anchor_x="center",
            anchor_y="top",
            font_name="Arial",
            bold=True
        )
    
    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense)
        self.hp -= actual_damage
        return actual_damage
    
    def is_alive(self):
        return self.hp > 0