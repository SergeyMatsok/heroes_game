import random

# Типы предметов
ITEM_TYPE_WEAPON = "weapon"
ITEM_TYPE_ARMOR = "armor"
ITEM_TYPE_ACCESSORY = "accessory"
ITEM_TYPE_CONSUMABLE = "consumable"

# Редкость
RARITY_COMMON = "common"
RARITY_RARE = "rare"
RARITY_EPIC = "epic"
RARITY_LEGENDARY = "legendary"

RARITY_COLORS = {
    RARITY_COMMON: (200, 200, 200),      # Серый
    RARITY_RARE: (50, 150, 255),         # Синий
    RARITY_EPIC: (180, 50, 255),         # Фиолетовый
    RARITY_LEGENDARY: (255, 200, 0)      # Золотой
}

RARITY_NAMES = {
    RARITY_COMMON: "Обычный",
    RARITY_RARE: "Редкий",
    RARITY_EPIC: "Эпический",
    RARITY_LEGENDARY: "Легендарный"
}

# Базы предметов
WEAPONS = [
    {"name": "Ржавый меч", "attack": 3, "rarity": RARITY_COMMON},
    {"name": "Стальной меч", "attack": 6, "rarity": RARITY_COMMON},
    {"name": "Острый клинок", "attack": 10, "rarity": RARITY_RARE},
    {"name": "Меч паладина", "attack": 15, "rarity": RARITY_RARE},
    {"name": "Драконий клинок", "attack": 22, "rarity": RARITY_EPIC},
    {"name": "Меч Архангела", "attack": 30, "rarity": RARITY_LEGENDARY},
    {"name": "Боевой топор", "attack": 8, "rarity": RARITY_COMMON},
    {"name": "Топор викинга", "attack": 14, "rarity": RARITY_RARE},
    {"name": "Лук эльфа", "attack": 12, "rarity": RARITY_RARE},
    {"name": "Посох мага", "attack": 18, "rarity": RARITY_EPIC},
]

ARMORS = [
    {"name": "Тряпичная одежда", "defense": 2, "hp": 10, "rarity": RARITY_COMMON},
    {"name": "Кожаная броня", "defense": 4, "hp": 20, "rarity": RARITY_COMMON},
    {"name": "Кольчуга", "defense": 7, "hp": 30, "rarity": RARITY_RARE},
    {"name": "Латный доспех", "defense": 12, "hp": 50, "rarity": RARITY_RARE},
    {"name": "Драконья чешуя", "defense": 18, "hp": 80, "rarity": RARITY_EPIC},
    {"name": "Броня титана", "defense": 25, "hp": 120, "rarity": RARITY_LEGENDARY},
    {"name": "Шлем воина", "defense": 3, "hp": 15, "rarity": RARITY_COMMON},
    {"name": "Щит стража", "defense": 8, "hp": 40, "rarity": RARITY_RARE},
]

ACCESSORIES = [
    {"name": "Кольцо силы", "attack": 5, "rarity": RARITY_RARE},
    {"name": "Кольцо защиты", "defense": 5, "rarity": RARITY_RARE},
    {"name": "Амулет жизни", "hp": 50, "rarity": RARITY_RARE},
    {"name": "Перстень могущества", "attack": 10, "defense": 5, "rarity": RARITY_EPIC},
    {"name": "Амулет дракона", "attack": 8, "hp": 60, "rarity": RARITY_EPIC},
    {"name": "Кольцо бессмертия", "hp": 100, "rarity": RARITY_LEGENDARY},
]


class Item:
    def __init__(self, name, item_type, rarity, **stats):
        self.name = name
        self.type = item_type
        self.rarity = rarity
        self.attack = stats.get("attack", 0)
        self.defense = stats.get("defense", 0)
        self.hp = stats.get("hp", 0)
        self.value = self.calculate_value()
    
    def calculate_value(self):
        """Рассчитывает стоимость предмета"""
        base_value = (self.attack * 15 + self.defense * 12 + self.hp * 2)
        rarity_multiplier = {
            RARITY_COMMON: 1,
            RARITY_RARE: 2.5,
            RARITY_EPIC: 5,
            RARITY_LEGENDARY: 10
        }
        return int(base_value * rarity_multiplier.get(self.rarity, 1))
    
    def get_description(self):
        """Возвращает описание предмета"""
        stats = []
        if self.attack > 0:
            stats.append(f"⚔️ +{self.attack}")
        if self.defense > 0:
            stats.append(f"🛡️ +{self.defense}")
        if self.hp > 0:
            stats.append(f"❤️ +{self.hp}")
        
        rarity_name = RARITY_NAMES.get(self.rarity, "Неизвестный")
        type_name = {
            ITEM_TYPE_WEAPON: "Оружие",
            ITEM_TYPE_ARMOR: "Броня",
            ITEM_TYPE_ACCESSORY: "Аксессуар"
        }.get(self.type, "Предмет")
        
        return f"{self.name}\n{type_name} ({rarity_name})\n{' | '.join(stats)}"
    
    def get_color(self):
        """Возвращает цвет предмета"""
        return RARITY_COLORS.get(self.rarity, (255, 255, 255))

    def get_icon(self):
        """Возвращает текстуру иконки предмета"""
        from item_icons import load_item_icon
        return load_item_icon(self.type, self.rarity)


def generate_random_item(min_week=1, max_week=3):
    """Генерирует случайный предмет"""
    # Определяем редкость на основе недели
    roll = random.random()
    if roll < 0.6:
        rarity = RARITY_COMMON
        pool = WEAPONS + ARMORS
    elif roll < 0.85:
        rarity = RARITY_RARE
        pool = WEAPONS + ARMORS + ACCESSORIES
    elif roll < 0.97:
        rarity = RARITY_EPIC
        pool = WEAPONS + ARMORS + ACCESSORIES
    else:
        rarity = RARITY_LEGENDARY
        pool = WEAPONS + ARMORS + ACCESSORIES
    
    # Выбираем случайный предмет из пула
    base_item = random.choice(pool)
    
    # Создаём предмет
    if base_item in WEAPONS:
        item_type = ITEM_TYPE_WEAPON
    elif base_item in ARMORS:
        item_type = ITEM_TYPE_ARMOR
    else:
        item_type = ITEM_TYPE_ACCESSORY


    return Item(
        name=base_item["name"],
        item_type=item_type,
        rarity=rarity,
        attack=base_item.get("attack", 0),
        defense=base_item.get("defense", 0),
        hp=base_item.get("hp", 0)
    )
        

