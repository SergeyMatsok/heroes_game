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
# Базы предметов (эпические ВСЕГДА лучше обычных)
WEAPONS = [
    # Обычные
    {"name": "Ржавый меч", "attack": 3, "rarity": "common"},
    {"name": "Стальной меч", "attack": 6, "rarity": "common"},
    {"name": "Боевой топор", "attack": 8, "rarity": "common"},
    
    # Редкие (минимум +10)
    {"name": "Острый клинок", "attack": 10, "rarity": "rare"},
    {"name": "Меч паладина", "attack": 13, "rarity": "rare"},
    {"name": "Топор викинга", "attack": 15, "rarity": "rare"},
    {"name": "Лук эльфа", "attack": 12, "rarity": "rare"},
    
    # Эпические (минимум +18)
    {"name": "Драконий клинок", "attack": 20, "rarity": "epic"},
    {"name": "Меч Архангела", "attack": 25, "rarity": "epic"},
    {"name": "Посох мага", "attack": 18, "rarity": "epic"},
    
    # Легендарные (минимум +30)
    {"name": "Клинок Бессмертия", "attack": 35, "rarity": "legendary"},
    {"name": "Меч Бога Войны", "attack": 40, "rarity": "legendary"},
]

ARMORS = [
    # Обычные
    {"name": "Тряпичная одежда", "defense": 2, "hp": 10, "rarity": "common"},
    {"name": "Кожаная броня", "defense": 4, "hp": 20, "rarity": "common"},
    {"name": "Шлем воина", "defense": 3, "hp": 15, "rarity": "common"},
    
    # Редкие (минимум +7/30)
    {"name": "Кольчуга", "defense": 7, "hp": 30, "rarity": "rare"},
    {"name": "Латный доспех", "defense": 10, "hp": 45, "rarity": "rare"},
    {"name": "Щит стража", "defense": 8, "hp": 40, "rarity": "rare"},
    
    # Эпические (минимум +15/70)
    {"name": "Драконья чешуя", "defense": 16, "hp": 70, "rarity": "epic"},
    {"name": "Броня титана", "defense": 20, "hp": 90, "rarity": "epic"},
    
    # Легендарные (минимум +25/120)
    {"name": "Доспех Бога", "defense": 28, "hp": 130, "rarity": "legendary"},
]

ACCESSORIES = [
    # Редкие
    {"name": "Кольцо силы", "attack": 5, "rarity": "rare"},
    {"name": "Кольцо защиты", "defense": 5, "rarity": "rare"},
    {"name": "Амулет жизни", "hp": 50, "rarity": "rare"},
    
    # Эпические (минимум +8/60)
    {"name": "Перстень могущества", "attack": 10, "defense": 5, "rarity": "epic"},
    {"name": "Амулет дракона", "attack": 8, "hp": 60, "rarity": "epic"},
    
    # Легендарные
    {"name": "Кольцо бессмертия", "hp": 100, "rarity": "legendary"},
    {"name": "Амулет Власти", "attack": 12, "defense": 8, "rarity": "legendary"},
]


class Item:
    def __init__(self, name, item_type, rarity, **stats):
        self.name = name
        self.type = item_type
        self.rarity = rarity
        self.attack = stats.get("attack", 0)
        self.defense = stats.get("defense", 0)
        self.hp = stats.get("hp", 0)
        
        # ПРОВЕРКА: эпические не могут быть слабее обычных
        self._validate_stats()
        
        self.value = self.calculate_value()
    
    def _validate_stats(self):
        """Проверяет что статы соответствуют редкости"""
        min_stats = {
            "common": {"attack": 0, "defense": 0, "hp": 0},
            "rare": {"attack": 8, "defense": 5, "hp": 25},
            "epic": {"attack": 15, "defense": 12, "hp": 60},
            "legendary": {"attack": 25, "defense": 20, "hp": 100}
        }
        
        rarity_min = min_stats.get(self.rarity, {})
        
        if self.attack > 0 and self.attack < rarity_min.get("attack", 0):
            self.attack = rarity_min["attack"]
        
        if self.defense > 0 and self.defense < rarity_min.get("defense", 0):
            self.defense = rarity_min["defense"]
        
        if self.hp > 0 and self.hp < rarity_min.get("hp", 0):
            self.hp = rarity_min["hp"]
    
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
    """Генерирует случайный предмет с учётом редкости"""
    import random
    
    # Шансы редкости
    rarity_roll = random.random()
    if rarity_roll < 0.50:  # 50% обычный
        rarity = "common"
        stat_multiplier = 1.0
    elif rarity_roll < 0.80:  # 30% редкий
        rarity = "rare"
        stat_multiplier = 2.0
    elif rarity_roll < 0.95:  # 15% эпический
        rarity = "epic"
        stat_multiplier = 3.5
    else:  # 5% легендарный
        rarity = "legendary"
        stat_multiplier = 5.0
    
    # Выбираем тип предмета
    item_type_roll = random.random()
    if item_type_roll < 0.40:
        item_type = ITEM_TYPE_WEAPON
        base_list = WEAPONS
    elif item_type_roll < 0.75:
        item_type = ITEM_TYPE_ARMOR
        base_list = ARMORS
    else:
        item_type = ITEM_TYPE_ACCESSORY
        base_list = ACCESSORIES
    
    # Выбираем базовый предмет
    base_item = random.choice(base_list)
    
    # Усиливаем статы в зависимости от редкости
    if item_type == ITEM_TYPE_WEAPON:
        attack = int(base_item.get("attack", 5) * stat_multiplier)
        item = Item(
            name=base_item["name"],
            item_type=item_type,
            rarity=rarity,
            attack=attack
        )
    elif item_type == ITEM_TYPE_ARMOR:
        defense = int(base_item.get("defense", 3) * stat_multiplier)
        hp = int(base_item.get("hp", 10) * stat_multiplier)
        item = Item(
            name=base_item["name"],
            item_type=item_type,
            rarity=rarity,
            defense=defense,
            hp=hp
        )
    else:  # ACCESSORY
        # Аксессуары могут давать разные бонусы
        bonus_type = random.choice(["attack", "defense", "hp", "mixed"])
        if bonus_type == "attack":
            attack = int(base_item.get("attack", 3) * stat_multiplier)
            item = Item(name=base_item["name"], item_type=item_type, rarity=rarity, attack=attack)
        elif bonus_type == "defense":
            defense = int(base_item.get("defense", 3) * stat_multiplier)
            item = Item(name=base_item["name"], item_type=item_type, rarity=rarity, defense=defense)
        elif bonus_type == "hp":
            hp = int(base_item.get("hp", 15) * stat_multiplier)
            item = Item(name=base_item["name"], item_type=item_type, rarity=rarity, hp=hp)
        else:  # mixed
            attack = int(base_item.get("attack", 2) * stat_multiplier * 0.6)
            defense = int(base_item.get("defense", 2) * stat_multiplier * 0.6)
            hp = int(base_item.get("hp", 10) * stat_multiplier * 0.6)
            item = Item(name=base_item["name"], item_type=item_type, rarity=rarity, 
                       attack=attack, defense=defense, hp=hp)
    
    return item
        

