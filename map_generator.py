import random
from settings import MAP_WIDTH, MAP_HEIGHT, TERRAIN_GRASS, TERRAIN_MOUNTAIN, TERRAIN_WATER, TERRAIN_FOREST, GOLD_COUNT, POTION_COUNT

def generate_map():
    game_map = [[TERRAIN_GRASS for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    
    # Генерируем Горы (кластерами) - увеличено количество
    for _ in range(40):
        cx, cy = random.randint(3, MAP_WIDTH - 4), random.randint(3, MAP_HEIGHT - 4)
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if random.random() > 0.3:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < MAP_HEIGHT and 0 <= nx < MAP_WIDTH:
                        game_map[ny][nx] = TERRAIN_MOUNTAIN

    # Генерируем Воду (озера)
    for _ in range(20):
        cx, cy = random.randint(3, MAP_WIDTH - 4), random.randint(3, MAP_HEIGHT - 4)
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if random.random() > 0.4:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < MAP_HEIGHT and 0 <= nx < MAP_WIDTH and game_map[ny][nx] == TERRAIN_GRASS:
                        game_map[ny][nx] = TERRAIN_WATER

    # Генерируем Лес
    for _ in range(150):
        x, y = random.randint(0, MAP_WIDTH - 1), random.randint(0, MAP_HEIGHT - 1)
        if game_map[y][x] == TERRAIN_GRASS:
            game_map[y][x] = TERRAIN_FOREST

    # Гарантируем безопасную зону для старта героя (5x5)
    for y in range(5):
        for x in range(5):
            game_map[y][x] = TERRAIN_GRASS

    return game_map

def generate_gold_positions(game_map, hero_x, hero_y):
    gold_positions = []
    for _ in range(GOLD_COUNT):
        for attempt in range(200): # Увеличили попытки для большой карты
            x = random.randint(0, MAP_WIDTH - 1)
            y = random.randint(0, MAP_HEIGHT - 1)
            if game_map[y][x] in (TERRAIN_GRASS, TERRAIN_FOREST) and (x, y) not in gold_positions:
                if (x, y) != (hero_x, hero_y):
                    gold_positions.append((x, y))
                    break
    return gold_positions

def generate_potion_positions(game_map, hero_x, hero_y, gold_positions):
    potion_positions = []
    for _ in range(POTION_COUNT):
        for attempt in range(200):
            x = random.randint(0, MAP_WIDTH - 1)
            y = random.randint(0, MAP_HEIGHT - 1)
            if game_map[y][x] in (TERRAIN_GRASS, TERRAIN_FOREST) and (x, y) not in gold_positions and (x, y) not in potion_positions:
                if (x, y) != (hero_x, hero_y):
                    potion_positions.append((x, y))
                    break
    return potion_positions