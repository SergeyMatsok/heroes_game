import random
import os
import arcade
from settings import TERRAIN_GRASS, TERRAIN_FOREST, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, TERRAIN_PATH

# Типы объектов
OBJECT_NONE = 0
OBJECT_GOLD = 1
OBJECT_POTION = 2
OBJECT_CHEST = 3
OBJECT_MINE = 4
OBJECT_TAVERN = 5
OBJECT_TEMPLE = 6
OBJECT_RUINS = 7
OBJECT_SHRINE = 8
OBJECT_DRAGON_LAIR = 9
OBJECT_WATCHTOWER = 10
OBJECT_MERCHANT = 11
OBJECT_MAGIC_WELL = 12

class MapObject:
    def __init__(self, x, y, obj_type, value=0, permanent=False):
        self.x = x
        self.y = y
        self.type = obj_type
        self.value = value
        self.collected = False
        self.permanent = permanent  # НОВОЕ: не исчезает после использования
        self.texture = None
        self._load_texture()
    
    def get_name(self):
        """Возвращает название объекта для подсказки"""
        names = {
            OBJECT_GOLD: "Золото",
            OBJECT_POTION: "Зелье здоровья",
            OBJECT_CHEST: "Сундук с сокровищами",
            OBJECT_MINE: "Шахта",
            OBJECT_TAVERN: "Таверна (восстанавливает HP)",
            OBJECT_TEMPLE: "Храм (восстанавливает HP)",
            OBJECT_RUINS: "Руины",
            OBJECT_SHRINE: "Святилище",
            OBJECT_DRAGON_LAIR: "Логово дракона",
            OBJECT_WATCHTOWER: "Сторожевая башня",
            OBJECT_MERCHANT: "Магазин",
            OBJECT_MAGIC_WELL: "Магический колодец"
        }
        return names.get(self.type, "Неизвестно")
    
    def _load_texture(self):
        """Загружает текстуру объекта"""
        texture_names = {
            OBJECT_GOLD: "gold_pile",
            OBJECT_POTION: "health_potion",
            OBJECT_CHEST: "treasure_chest",
            OBJECT_MINE: "mine",
            OBJECT_TAVERN: "tavern",
            OBJECT_TEMPLE: "temple",
            OBJECT_RUINS: "ruins",
            OBJECT_SHRINE: "shrine",
            OBJECT_DRAGON_LAIR: "dragon_lair",
            OBJECT_WATCHTOWER: "watchtower",
            OBJECT_MERCHANT: "merchant",
            OBJECT_MAGIC_WELL: "magic_well"
        }
        
        texture_name = texture_names.get(self.type, "unknown")
        texture_path = f"images/objects/{texture_name}.png"
        
        try:
            if os.path.exists(texture_path):
                self.texture = arcade.load_texture(texture_path)
        except Exception as e:
            print(f"⚠️ Не удалось загрузить текстуру {texture_path}: {e}")
    
    def get_icon(self):
        """Возвращает эмодзи как fallback"""
        icons = {
            OBJECT_GOLD: "💰",
            OBJECT_POTION: "🧪",
            OBJECT_CHEST: "📦",
            OBJECT_MINE: "⛏️",
            OBJECT_TAVERN: "🍺",
            OBJECT_TEMPLE: "⛪",
            OBJECT_RUINS: "🏛️",
            OBJECT_SHRINE: "🗿",
            OBJECT_DRAGON_LAIR: "🐉",
            OBJECT_WATCHTOWER: "🗼",
            OBJECT_MERCHANT: "🏪",
            OBJECT_MAGIC_WELL: "⛲"
        }
        return icons.get(self.type, "?")
    
    def draw(self, screen_x, screen_y):
        """Рисует объект на экране"""
        if self.texture:
            # Размер объекта — почти вся клетка (клетка 64x64)
            MAX_SIZE = 56
            
            # Вычисляем масштаб
            scale = min(MAX_SIZE / self.texture.width, MAX_SIZE / self.texture.height)
            
            width = int(self.texture.width * scale)
            height = int(self.texture.height * scale)
            
            # Центр клетки — XYWH использует именно центр!
            center_x = screen_x + TILE_SIZE // 2
            center_y = screen_y + TILE_SIZE // 2
            
            # XYWH = (center_x, center_y, width, height)
            rect = arcade.XYWH(center_x, center_y, width, height)
            arcade.draw_texture_rect(self.texture, rect)
        else:
            # Fallback на эмодзи
            arcade.draw_text(
                self.get_icon(),
                screen_x + TILE_SIZE // 2,
                screen_y + TILE_SIZE // 2,
                arcade.color.WHITE,
                28,
                anchor_x="center",
                anchor_y="center"
            )

def generate_map_objects(game_map, hero_x, hero_y):
    """Генерирует все объекты на карте"""
    objects = []
    
    # Золото (30 штук)
    for _ in range(30):
        x, y = get_random_position(game_map, hero_x, hero_y, objects)
        if x is not None:
            objects.append(MapObject(x, y, OBJECT_GOLD))
    
    # Зелья (15 штук)
    for _ in range(15):
        x, y = get_random_position(game_map, hero_x, hero_y, objects)
        if x is not None:
            objects.append(MapObject(x, y, OBJECT_POTION))
    
    # Сундуки с сокровищами (8 штук)
    for _ in range(8):
        x, y = get_random_position(game_map, hero_x, hero_y, objects)
        if x is not None:
            chest = MapObject(x, y, OBJECT_CHEST, value=random.randint(100, 300))
            objects.append(chest)
    
    # Шахты (3 штуки)
    for _ in range(3):
        x, y = get_random_position(game_map, hero_x, hero_y, objects)
        if x is not None:
            objects.append(MapObject(x, y, OBJECT_MINE))
    
    # Таверны (2 штуки) - ПОСТОЯННЫЕ
    for _ in range(2):
        x, y = get_random_position(game_map, hero_x, hero_y, objects)
        if x is not None:
            objects.append(MapObject(x, y, OBJECT_TAVERN, permanent=True))
    
    # Храмы (2 штуки) - ПОСТОЯННЫЕ
    for _ in range(2):
        x, y = get_random_position(game_map, hero_x, hero_y, objects)
        if x is not None:
            objects.append(MapObject(x, y, OBJECT_TEMPLE, permanent=True))
    
    # Руины (4 штуки)
    for _ in range(4):
        x, y = get_random_position(game_map, hero_x, hero_y, objects)
        if x is not None:
            objects.append(MapObject(x, y, OBJECT_RUINS))
    
    # Святилища (3 штуки)
    for _ in range(3):
        x, y = get_random_position(game_map, hero_x, hero_y, objects)
        if x is not None:
            objects.append(MapObject(x, y, OBJECT_SHRINE))
    
    # Логово дракона (1 штука)
    x, y = get_random_position(game_map, hero_x, hero_y, objects)
    if x is not None:
        objects.append(MapObject(x, y, OBJECT_DRAGON_LAIR))
    
    # Сторожевые башни (5 штук)
    for _ in range(5):
        x, y = get_random_position(game_map, hero_x, hero_y, objects)
        if x is not None:
            objects.append(MapObject(x, y, OBJECT_WATCHTOWER))
    
    # Торговцы (3 штуки) - ПОСТОЯННЫЕ
    for _ in range(3):
        x, y = get_random_position(game_map, hero_x, hero_y, objects)
        if x is not None:
            objects.append(MapObject(x, y, OBJECT_MERCHANT, permanent=True))
    
    # Магические колодцы (3 штуки)
    for _ in range(3):
        x, y = get_random_position(game_map, hero_x, hero_y, objects)
        if x is not None:
            objects.append(MapObject(x, y, OBJECT_MAGIC_WELL))
    
    return objects


def get_random_position(game_map, hero_x, hero_y, objects, max_attempts=100):
    """Находит случайную позицию для объекта"""
    for _ in range(max_attempts):
        x = random.randint(0, MAP_WIDTH - 1)
        y = random.randint(0, MAP_HEIGHT - 1)
        
        # Проверяем что это проходимая местность
        if game_map[y][x] not in (TERRAIN_GRASS, TERRAIN_FOREST, TERRAIN_PATH):  # ← ДОБАВЬ
            continue
        
        # Не слишком близко к герою
        if abs(x - hero_x) + abs(y - hero_y) < 5:
            continue
        
        # Не на существующем объекте
        if any(obj.x == x and obj.y == y for obj in objects):
            continue
        
        return x, y
    
    return None, None