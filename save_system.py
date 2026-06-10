import json
import os
from settings import MAP_WIDTH, MAP_HEIGHT

SAVE_DIR = "saves"
SAVE_FILE = os.path.join(SAVE_DIR, "autosave.json")

def ensure_save_dir():
    """Создаёт папку saves если её нет"""
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

def save_game(game):
    """Сохраняет текущее состояние игры"""
    ensure_save_dir()
    
    save_data = {
        # Герой
        "hero": {
            "x": game.hero.x,
            "y": game.hero.y,
            "level": game.hero.level,
            "xp": game.hero.xp,
            "xp_to_next_level": game.hero.xp_to_next_level,
            "hp": game.hero.hp,
            "max_hp": game.hero.max_hp,
            "gold": game.hero.gold,
            "attack": game.hero.attack,
            "defense": game.hero.defense
        },
        
        # Карта
        "game_map": game.game_map,
        
        # Ресурсы
        "gold_positions": list(game.gold_positions),
        "potion_positions": [(p.x, p.y) for p in game.potions],
        
        # Враги
        "enemies": [
            {
                "x": e.x,
                "y": e.y,
                "type": e.type,
                "spawn_week": e.spawn_week,
                "hp": e.hp,
                "max_hp": e.max_hp,
                "attack": e.attack,
                "defense": e.defense,
                "is_aggroed": e.is_aggroed
            }
            for e in game.enemies
        ],
        
        # Квесты
        "quests": [
            {
                "type": q.type,
                "target": q.target,
                "required": q.required,
                "current": q.current,
                "reward_gold": q.reward_gold,
                "reward_xp": q.reward_xp,
                "week": q.week,
                "completed": q.completed
            }
            for q in game.quests
        ],
        "completed_quests_count": len(game.completed_quests),
        
        # Прогресс
        "turns": game.turns,
        "game_over": game.game_over,
        "victory": game.victory,
        
        # Туман войны
        "fog": game.fog,
        
        # Статистика
        "tiles_explored": game.tiles_explored,
        "total_gold_collected": game.total_gold_collected,
        "total_potions_collected": game.total_potions_collected,
        "enemies_killed_by_type": game.enemies_killed_by_type
    }
    
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Игра сохранена в {SAVE_FILE}")
    return True

def load_game(game):
    """Загружает состояние игры"""
    if not os.path.exists(SAVE_FILE):
        print("❌ Файл сохранения не найден!")
        return False
    
    with open(SAVE_FILE, 'r', encoding='utf-8') as f:
        save_data = json.load(f)
    
    # Восстанавливаем героя
    hero_data = save_data["hero"]
    game.hero.x = hero_data["x"]
    game.hero.y = hero_data["y"]
    game.hero.level = hero_data["level"]
    game.hero.xp = hero_data["xp"]
    game.hero.xp_to_next_level = hero_data["xp_to_next_level"]
    game.hero.hp = hero_data["hp"]
    game.hero.max_hp = hero_data["max_hp"]
    game.hero.gold = hero_data["gold"]
    game.hero.attack = hero_data["attack"]
    game.hero.defense = hero_data["defense"]
    
    # Восстанавливаем карту
    game.game_map = save_data["game_map"]
    
    # Восстанавливаем ресурсы
    game.gold_positions = [tuple(pos) for pos in save_data["gold_positions"]]
    game.potions = []
    for pos in save_data["potion_positions"]:
        from potion import Potion
        game.potions.append(Potion(pos[0], pos[1]))
    
    # Восстанавливаем врагов
    game.enemies = []
    for e_data in save_data["enemies"]:
        from enemy import Enemy
        enemy = Enemy(e_data["x"], e_data["y"], e_data["type"], e_data["spawn_week"])
        enemy.hp = e_data["hp"]
        enemy.max_hp = e_data["max_hp"]
        enemy.attack = e_data["attack"]
        enemy.defense = e_data["defense"]
        enemy.is_aggroed = e_data["is_aggroed"]
        game.enemies.append(enemy)
    
    # Восстанавливаем квесты
    game.quests = []
    for q_data in save_data["quests"]:
        from quest import Quest
        quest = Quest(
            q_data["type"],
            q_data["target"],
            q_data["required"],
            q_data["reward_gold"],
            q_data["reward_xp"],
            q_data["week"]
        )
        quest.current = q_data["current"]
        quest.completed = q_data["completed"]
        game.quests.append(quest)
    
    # Восстанавливаем прогресс
    game.turns = save_data["turns"]
    game.game_over = save_data["game_over"]
    game.victory = save_data["victory"]
    
    # Восстанавливаем туман
    game.fog = save_data["fog"]
    
    # Восстанавливаем статистику
    game.tiles_explored = save_data["tiles_explored"]
    game.total_gold_collected = save_data["total_gold_collected"]
    game.total_potions_collected = save_data["total_potions_collected"]
    game.enemies_killed_by_type = save_data["enemies_killed_by_type"]
    
    # Обновляем камеру
    game.update_camera()
    
    print(f"📂 Игра загружена из {SAVE_FILE}")
    game.log_message("📂 Игра загружена!")
    return True