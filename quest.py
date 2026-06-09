import random
from settings import (
    GOLD_PER_PILE, XP_PER_KILL
)

# Типы квестов
QUEST_KILL_ENEMIES = "kill"
QUEST_COLLECT_GOLD = "collect_gold"
QUEST_COLLECT_POTIONS = "collect_potions"
QUEST_EXPLORE_TILES = "explore"

class Quest:
    def __init__(self, quest_type, target, required, reward_gold, reward_xp, week):
        self.type = quest_type
        self.target = target  # тип врага или предмета
        self.required = required
        self.current = 0
        self.reward_gold = reward_gold
        self.reward_xp = reward_xp
        self.week = week  # неделя выдачи
        self.completed = False
        
        # Иконки для типов
        self.icons = {
            "wolf": "🐺",
            "goblin": "👺",
            "skeleton": "💀",
            "lich": "🧙",
            "golem": "🗿",
            "dragon": "🐉",
            "gold": "💰",
            "potion": "🧪",
            "explore": "🗺️"
        }
    
    def get_description(self):
        """Возвращает описание квеста"""
        icon = self.icons.get(self.target, "❓")
        
        if self.type == QUEST_KILL_ENEMIES:
            enemy_names = {
                "wolf": "волков",
                "goblin": "гоблинов",
                "skeleton": "скелетов",
                "lich": "личей",
                "golem": "големов",
                "dragon": "драконов"
            }
            name = enemy_names.get(self.target, self.target)
            return f"📜 Убить {self.required} {name} {icon}"
        
        elif self.type == QUEST_COLLECT_GOLD:
            return f"📜 Собрать {self.required} золота {icon}"
        
        elif self.type == QUEST_COLLECT_POTIONS:
            return f"📜 Найти {self.required} зелий {icon}"
        
        elif self.type == QUEST_EXPLORE_TILES:
            return f"📜 Исследовать {self.required} клеток {icon}"
        
        return "Неизвестный квест"
    
    def get_progress_text(self):
        """Возвращает текст прогресса"""
        return f"{self.current}/{self.required}"
    
    def is_completed(self):
        """Проверяет выполнение"""
        return self.current >= self.required
    
    def add_progress(self, amount=1):
        """Добавляет прогресс"""
        if not self.completed:
            self.current += amount
            if self.is_completed():
                self.completed = True
                return True  # Квест только что выполнен
        return False
    
    def get_reward_text(self):
        """Возвращает текст награды"""
        rewards = []
        if self.reward_gold > 0:
            rewards.append(f"{self.reward_gold}💰")
        if self.reward_xp > 0:
            rewards.append(f"{self.reward_xp}⭐")
        return " | ".join(rewards)


def generate_weekly_quests(week, player_level):
    """Генерирует 2-3 случайных квеста на неделю"""
    quests = []
    num_quests = random.randint(2, 3)
    
    # Доступные типы врагов (зависит от недели)
    available_enemies = ["wolf", "goblin"]
    if week >= 2:
        available_enemies.append("skeleton")
    if week >= 3:
        available_enemies.extend(["lich", "golem"])
    if week >= 5:
        available_enemies.append("dragon")
    
    for i in range(num_quests):
        quest_type = random.choice([
            QUEST_KILL_ENEMIES,
            QUEST_COLLECT_GOLD,
            QUEST_COLLECT_POTIONS,
            QUEST_EXPLORE_TILES
        ])
        
        # Базовые значения наград
        base_gold = 50 * week
        base_xp = 30 * week
        
        if quest_type == QUEST_KILL_ENEMIES:
            enemy = random.choice(available_enemies)
            # Количество зависит от силы врага
            if enemy == "dragon":
                required = random.randint(1, 2)
                reward_gold = base_gold * 3
                reward_xp = base_xp * 3
            elif enemy in ["lich", "golem"]:
                required = random.randint(3, 5)
                reward_gold = base_gold * 2
                reward_xp = base_xp * 2
            else:
                required = random.randint(5, 10)
                reward_gold = base_gold
                reward_xp = base_xp
            
            quest = Quest(QUEST_KILL_ENEMIES, enemy, required, reward_gold, reward_xp, week)
        
        elif quest_type == QUEST_COLLECT_GOLD:
            required = random.randint(100, 300) * week
            quest = Quest(QUEST_COLLECT_GOLD, "gold", required, base_gold, base_xp, week)
        
        elif quest_type == QUEST_COLLECT_POTIONS:
            required = random.randint(2, 5)
            quest = Quest(QUEST_COLLECT_POTIONS, "potion", required, base_gold, base_xp, week)
        
        else:  # QUEST_EXPLORE_TILES
            required = random.randint(20, 40)
            quest = Quest(QUEST_EXPLORE_TILES, "explore", required, base_gold, base_xp, week)
        
        quests.append(quest)
    
    return quests