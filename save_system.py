import json
import os
from map_objects import MapObject, OBJECT_GOLD, OBJECT_POTION, OBJECT_CHEST, OBJECT_MINE, OBJECT_TAVERN, OBJECT_TEMPLE, OBJECT_RUINS, OBJECT_SHRINE, OBJECT_DRAGON_LAIR, OBJECT_WATCHTOWER, OBJECT_MERCHANT, OBJECT_MAGIC_WELL
from settings import MAP_WIDTH, MAP_HEIGHT

SAVE_FILE = "save.json"

def save_game(game):
    """Сохраняет игру в JSON файл"""
    try:
        save_data = {
            "turns": game.turns,
            "hero": {
                "x": game.hero.x,
                "y": game.hero.y,
                "hp": game.hero.hp,
                "max_hp": game.hero.max_hp,
                "attack": game.hero.attack,
                "defense": game.hero.defense,
                "gold": game.hero.gold,
                "level": game.hero.level,
                "xp": game.hero.xp,
                "xp_to_next": game.hero.xp_to_next,
                "attack_upgrades": game.hero.attack_upgrades,
                "defense_upgrades": game.hero.defense_upgrades,
                "hp_upgrades": game.hero.hp_upgrades,
                "inventory": [
                    {
                        "name": item.name,
                        "type": item.type,
                        "rarity": item.rarity,
                        "attack": item.attack,
                        "defense": item.defense,
                        "hp": item.hp
                    }
                    for item in game.hero.inventory
                ],
                "equipped_weapon": {
                    "name": game.hero.equipped_weapon.name,
                    "type": game.hero.equipped_weapon.type,
                    "rarity": game.hero.equipped_weapon.rarity,
                    "attack": game.hero.equipped_weapon.attack,
                    "defense": game.hero.equipped_weapon.defense,
                    "hp": game.hero.equipped_weapon.hp
                } if game.hero.equipped_weapon else None,
                "equipped_armor": {
                    "name": game.hero.equipped_armor.name,
                    "type": game.hero.equipped_armor.type,
                    "rarity": game.hero.equipped_armor.rarity,
                    "attack": game.hero.equipped_armor.attack,
                    "defense": game.hero.equipped_armor.defense,
                    "hp": game.hero.equipped_armor.hp
                } if game.hero.equipped_armor else None,
                "equipped_accessory": {
                    "name": game.hero.equipped_accessory.name,
                    "type": game.hero.equipped_accessory.type,
                    "rarity": game.hero.equipped_accessory.rarity,
                    "attack": game.hero.equipped_accessory.attack,
                    "defense": game.hero.equipped_accessory.defense,
                    "hp": game.hero.equipped_accessory.hp
                } if game.hero.equipped_accessory else None,
            },
            "map_objects": [
                {
                    "x": obj.x,
                    "y": obj.y,
                    "type": obj.type,
                    "value": obj.value,
                    "collected": obj.collected
                }
                for obj in game.map_objects
            ],
            "items_on_map": [
                {
                    "x": item.x,
                    "y": item.y,
                    "name": item.name,
                    "type": item.type,
                    "rarity": item.rarity,
                    "attack": item.attack,
                    "defense": item.defense,
                    "hp": item.hp
                }
                for item in game.items_on_map
            ],
            "enemies": [
                {
                    "x": enemy.x,
                    "y": enemy.y,
                    "type": enemy.type,
                    "spawn_week": enemy.spawn_week,
                    "hp": enemy.hp,
                    "max_hp": enemy.max_hp,
                    "attack": enemy.attack,
                    "defense": enemy.defense
                }
                for enemy in game.enemies
            ],
            "quests": [
                {
                    "type": quest.type,
                    "target": quest.target,
                    "progress": quest.progress,
                    "required": quest.required,
                    "reward_gold": quest.reward_gold,
                    "reward_xp": quest.reward_xp,
                    "completed": quest.completed
                }
                for quest in game.quests
            ],
            "fog": game.fog,
            "game_map": game.game_map,
            "enemies_killed_by_type": game.enemies_killed_by_type,
            "total_gold_collected": game.total_gold_collected,
            "total_potions_collected": game.total_potions_collected,
        }
        
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return False


def load_game(game):
    """Загружает игру из JSON файла"""
    if not os.path.exists(SAVE_FILE):
        print("️ Файл сохранения не найден!")
        return False
    
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            save_data = json.load(f)
        
        # Загружаем основные параметры
        game.turns = save_data["turns"]
        game.game_map = save_data["game_map"]
        game.fog = save_data["fog"]
        game.enemies_killed_by_type = save_data.get("enemies_killed_by_type", {})
        game.total_gold_collected = save_data.get("total_gold_collected", 0)
        game.total_potions_collected = save_data.get("total_potions_collected", 0)
        
        # Загружаем героя
        hero_data = save_data["hero"]
        game.hero.x = hero_data["x"]
        game.hero.y = hero_data["y"]
        game.hero.hp = hero_data["hp"]
        game.hero.max_hp = hero_data["max_hp"]
        game.hero.attack = hero_data["attack"]
        game.hero.defense = hero_data["defense"]
        game.hero.gold = hero_data["gold"]
        game.hero.level = hero_data["level"]
        game.hero.xp = hero_data["xp"]
        game.hero.xp_to_next = hero_data["xp_to_next"]
        game.hero.attack_upgrades = hero_data.get("attack_upgrades", 0)
        game.hero.defense_upgrades = hero_data.get("defense_upgrades", 0)
        game.hero.hp_upgrades = hero_data.get("hp_upgrades", 0)
        
        # Загружаем инвентарь
        from items import Item
        game.hero.inventory = []
        for item_data in hero_data.get("inventory", []):
            item = Item(
                name=item_data["name"],
                item_type=item_data["type"],
                rarity=item_data["rarity"],
                attack=item_data.get("attack", 0),
                defense=item_data.get("defense", 0),
                hp=item_data.get("hp", 0)
            )
            game.hero.inventory.append(item)
        
        # Загружаем экипировку
        game.hero.equipped_weapon = None
        game.hero.equipped_armor = None
        game.hero.equipped_accessory = None
        
        if hero_data.get("equipped_weapon"):
            w = hero_data["equipped_weapon"]
            game.hero.equipped_weapon = Item(w["name"], w["type"], w["rarity"], attack=w.get("attack", 0), defense=w.get("defense", 0), hp=w.get("hp", 0))
        
        if hero_data.get("equipped_armor"):
            a = hero_data["equipped_armor"]
            game.hero.equipped_armor = Item(a["name"], a["type"], a["rarity"], attack=a.get("attack", 0), defense=a.get("defense", 0), hp=a.get("hp", 0))
        
        if hero_data.get("equipped_accessory"):
            acc = hero_data["equipped_accessory"]
            game.hero.equipped_accessory = Item(acc["name"], acc["type"], acc["rarity"], attack=acc.get("attack", 0), defense=acc.get("defense", 0), hp=acc.get("hp", 0))
        
        game.hero.recalculate_bonuses()
        
        # Загружаем объекты карты
        game.map_objects = []
        for obj_data in save_data.get("map_objects", []):
            obj = MapObject(obj_data["x"], obj_data["y"], obj_data["type"], obj_data.get("value", 0))
            obj.collected = obj_data.get("collected", False)
            game.map_objects.append(obj)
        
        # Загружаем предметы на карте
        game.items_on_map = []
        for item_data in save_data.get("items_on_map", []):
            item = Item(
                name=item_data["name"],
                item_type=item_data["type"],
                rarity=item_data["rarity"],
                attack=item_data.get("attack", 0),
                defense=item_data.get("defense", 0),
                hp=item_data.get("hp", 0)
            )
            item.x = item_data["x"]
            item.y = item_data["y"]
            game.items_on_map.append(item)
        
        # Загружаем врагов
        from enemy import Enemy
        game.enemies = []
        for enemy_data in save_data.get("enemies", []):
            enemy = Enemy(
                enemy_data["x"],
                enemy_data["y"],
                enemy_data["type"],
                spawn_week=enemy_data.get("spawn_week", 1)
            )
            enemy.hp = enemy_data.get("hp", enemy.max_hp)
            enemy.max_hp = enemy_data.get("max_hp", enemy.max_hp)
            enemy.attack = enemy_data.get("attack", enemy.attack)
            enemy.defense = enemy_data.get("defense", enemy.defense)
            game.enemies.append(enemy)
        
        # Загружаем квесты
        from quest import Quest
        game.quests = []
        for quest_data in save_data.get("quests", []):
            quest = Quest(
                quest_type=quest_data["type"],
                target=quest_data.get("target"),
                required=quest_data["required"],
                reward_gold=quest_data["reward_gold"],
                reward_xp=quest_data["reward_xp"]
            )
            quest.progress = quest_data.get("progress", 0)
            quest.completed = quest_data.get("completed", False)
            game.quests.append(quest)
        
        game.update_camera()
        game.log_message("📂 Игра загружена!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        import traceback
        traceback.print_exc()
        return False