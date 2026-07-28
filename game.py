import random

import arcade

from combat_animation import CombatAnimator
from controls import draw_controls_panel
from enemy import Enemy
from hero import Hero
from inventory_ui import draw_inventory
from map_generator import (generate_gold_positions, generate_map,
                           generate_potion_positions)
from map_objects import (OBJECT_CHEST, OBJECT_DRAGON_LAIR, OBJECT_GOLD,
                         OBJECT_MAGIC_WELL, OBJECT_MERCHANT, OBJECT_MINE,
                         OBJECT_POTION, OBJECT_RUINS, OBJECT_SHRINE,
                         OBJECT_TAVERN, OBJECT_TEMPLE, OBJECT_WATCHTOWER,
                         generate_map_objects, get_random_position)
from potion import Potion
from quest import (QUEST_COLLECT_GOLD, QUEST_COLLECT_POTIONS,
                   QUEST_EXPLORE_TILES, QUEST_KILL_ENEMIES, Quest,
                   generate_weekly_quests)
from save_system import load_game, save_game
from settings import (COLOR_FOREST, COLOR_GOLD, COLOR_GRASS,
                      COLOR_GRASS_DETAIL, COLOR_GRID, COLOR_MOUNTAIN,
                      COLOR_MOUNTAIN_PEAK, COLOR_UI_BG, COLOR_WATER,
                      COLOR_WATER_WAVE, COLOR_PATH,  # ← ДОБАВЬ
                      ENEMIES_SPAWN_PER_WEEK,
                      ENEMY_AGGRO_RANGE, ENEMY_DRAGON_CHANCE,
                      ENEMY_DRAGON_COUNT, ENEMY_GOBLIN_CHANCE,
                      ENEMY_GOBLIN_COUNT, ENEMY_GOLEM_CHANCE,
                      ENEMY_GOLEM_COUNT, ENEMY_LICH_CHANCE, ENEMY_LICH_COUNT,
                      ENEMY_SKELETON_CHANCE, ENEMY_SKELETON_COUNT,
                      ENEMY_WOLF_CHANCE, ENEMY_WOLF_COUNT, GOLD_PER_PILE,
                      GOLD_SPAWN_PER_WEEK, HERO_ATTACK, HERO_DEFENSE,
                      HERO_START_HP, MAP_HEIGHT, MAP_WIDTH, MAX_ATTACK,
                      MAX_DEFENSE, MAX_HP, POTION_SPAWN_PER_WEEK,
                      SCREEN_HEIGHT, SCREEN_TITLE, SCREEN_WIDTH,
                      TERRAIN_FOREST, TERRAIN_GRASS, TERRAIN_MOUNTAIN,
                      TERRAIN_WATER, TERRAIN_PATH,  # ← ДОБАВЬ
                      TILE_SIZE, TURNS_PER_DAY, TURNS_PER_WEEK,
                      UPGRADE_AMOUNT, UPGRADE_ATTACK_COST,
                      UPGRADE_DEFENSE_COST, UPGRADE_HP_COST, WEEKS_TO_WIN,
                      XP_PER_KILL)

# Размеры областей
CONSOLE_WIDTH = 250       # Узкая консоль
UI_HEIGHT = 80
GAME_WIDTH = SCREEN_WIDTH - CONSOLE_WIDTH   # Оставшееся место
GAME_HEIGHT = SCREEN_HEIGHT - UI_HEIGHT     # Оставшееся место

class HeroesGame(arcade.Window):
    def __init__(self):
        super().__init__(1280, 800, SCREEN_TITLE, resizable=True)
        self.set_fullscreen(True)
        
        # ВАЖНО: принудительно пересчитываем размеры после полноэкранного режима
        # set_fullscreen может не сразу обновить self.width/height
        import time
        time.sleep(0.1)  # Даём время системе применить полноэкранный режим
        
        self.game_width = self.width - CONSOLE_WIDTH
        self.game_height = self.height - UI_HEIGHT
        

        
        self.camera_x = 0
        self.camera_y = 0
        
        self.messages = []
        self.max_messages = 8
        
        self.reset_game()
        self.quests = []
        self.completed_quests = []
        self.tiles_explored = 0
        self.total_gold_collected = 0
        self.total_potions_collected = 0
        self.enemies_killed_by_type = {}
        self.combat_animator = CombatAnimator()
        self.combat_state = None  # None или {'phase': 'hero_attack', 'timer': 0, ...}
        self.show_controls = False  # Показывать ли подсказки
        self.show_inventory = False
        self.mouse_x = 0
        self.mouse_y = 0
        self.hovered_object = None
        self.hovered_item = None
        self.hovered_enemy = None
        self.hovered_hero = False
        self.hovered_inventory_item = None
        self.hovered_equipment_item = None
        arcade.set_background_color((10, 10, 15))


    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.game_width = width - CONSOLE_WIDTH
        self.game_height = height - UI_HEIGHT
        
        self.update_camera()


    def log_message(self, text):
        self.messages.append(text)
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
        print(text)
    
    
    def reset_game(self):
        self.game_map = generate_map()
        self.hero = Hero(0, 0)
        self.game_map[self.hero.y][self.hero.x] = TERRAIN_GRASS
        
        # Генерируем все объекты на карте (включая золото и зелья)
        self.map_objects = generate_map_objects(self.game_map, self.hero.x, self.hero.y)
        
        self.enemies = self.generate_enemies()
        
        self.game_over = False
        self.victory = False
        self.shop_mode = False
        self.level_up_timer = 0
        self.turns = 0
        self.messages = []

        self.quests = []
        self.completed_quests = []
        self.tiles_explored = 0
        self.total_gold_collected = 0
        self.total_potions_collected = 0
        self.enemies_killed_by_type = {}
        self.terrain_textures = {}  # Кэш текстур местности
        self._load_terrain_textures()

        self.items_on_map = []
        
        # Генерируем случайные предметы экипировки
        for _ in range(10):
            x = random.randint(0, MAP_WIDTH - 1)
            y = random.randint(0, MAP_HEIGHT - 1)
            if self.game_map[y][x] in (TERRAIN_GRASS, TERRAIN_FOREST):
                from items import generate_random_item
                item = generate_random_item()
                item.x = x
                item.y = y
                self.items_on_map.append(item)
        
        self.fog = [[0 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
        self.update_fog()
        self.update_camera()
        self.log_message("🏰 Добро пожаловать в Бесконечное Королевство!")


    def _draw_hover_tooltips(self):
        """Рисует подсказки при наведении мыши"""
        tooltip_lines = []
        title_color = arcade.color.WHITE
        
        # Подсказка для предмета в инвентаре
        if self.hovered_inventory_item:
            item = self.hovered_inventory_item
            tooltip_lines = [f"🎁 {item.name}"]
            
            if item.attack > 0:
                tooltip_lines.append(f"⚔️ Атака: +{item.attack}")
            if item.defense > 0:
                tooltip_lines.append(f"️ Защита: +{item.defense}")
            if item.hp > 0:
                tooltip_lines.append(f"❤️ Здоровье: +{item.hp}")
            
            rarity_names = {"common": "Обычный", "rare": "Редкий", "epic": "Эпический", "legendary": "Легендарный"}
            tooltip_lines.append(f"📊 {rarity_names.get(item.rarity, item.rarity)}")
            
            # Цена продажи
            sell_price = self._get_item_sell_price(item)
            tooltip_lines.append(f"💰 Продажа: {sell_price} золота")
            
            if self.is_near_merchant():
                tooltip_lines.append(f"🖱️ ПКМ - продать")
            else:
                tooltip_lines.append(f"️ Найдите магазин для продажи")
            
            title_color = (255, 215, 0)
        
        # Подсказка для экипированного предмета
        elif self.hovered_equipment_item:
            item = self.hovered_equipment_item
            tooltip_lines = [f"️ {item.name} (экипировано)"]
            
            if item.attack > 0:
                tooltip_lines.append(f"⚔️ Атака: +{item.attack}")
            if item.defense > 0:
                tooltip_lines.append(f"🛡️ Защита: +{item.defense}")
            if item.hp > 0:
                tooltip_lines.append(f"❤️ Здоровье: +{item.hp}")
            
            rarity_names = {"common": "Обычный", "rare": "Редкий", "epic": "Эпический", "legendary": "Легендарный"}
            tooltip_lines.append(f"📊 {rarity_names.get(item.rarity, item.rarity)}")
            
            title_color = (100, 255, 100)
        
        # Подсказка для героя
        elif self.hovered_hero:
            tooltip_lines = [
                f"👤 Герой (Ур. {self.hero.level})",
                f"❤️ HP: {self.hero.hp}/{self.hero.max_hp}",
                f"⚔️ Атака: {self.hero.attack}",
                f"🛡️ Защита: {self.hero.defense}",
                f" Золото: {self.hero.gold}",
                f"⭐ Опыт: {self.hero.xp}"
            ]
            title_color = arcade.color.GREEN
        
        # Подсказка для объекта карты
        elif self.hovered_object:
            obj = self.hovered_object
            tooltip_lines = [f"📍 {obj.get_name()}"]
            
            from map_objects import (OBJECT_GOLD, OBJECT_POTION, OBJECT_CHEST, OBJECT_MINE,
                                     OBJECT_TAVERN, OBJECT_TEMPLE, OBJECT_RUINS, OBJECT_SHRINE,
                                     OBJECT_DRAGON_LAIR, OBJECT_WATCHTOWER, OBJECT_MERCHANT,
                                     OBJECT_MAGIC_WELL)
            
            if obj.type == OBJECT_GOLD:
                tooltip_lines.append(f"💰 {GOLD_PER_PILE} золота")
            elif obj.type == OBJECT_POTION:
                tooltip_lines.append(f" Восстанавливает 40 HP")
            elif obj.type == OBJECT_CHEST:
                tooltip_lines.append(f"📦 {obj.value} золота")
            elif obj.type == OBJECT_TAVERN:
                tooltip_lines.append(f"🍺 Полное восстановление HP")
            elif obj.type == OBJECT_TEMPLE:
                tooltip_lines.append(f"⛪ Полное восстановление HP")
            elif obj.type == OBJECT_MERCHANT:
                tooltip_lines.append(f"🏪 Нажмите M рядом чтобы открыть")
            elif obj.type == OBJECT_MINE:
                tooltip_lines.append(f"️ 50 золота")
            elif obj.type == OBJECT_RUINS:
                tooltip_lines.append(f"🏛️ Шанс найти предмет или золото")
            elif obj.type == OBJECT_SHRINE:
                tooltip_lines.append(f"🗿 Случайный бафф (+2 к характеристике)")
            elif obj.type == OBJECT_WATCHTOWER:
                tooltip_lines.append(f"🗼 Открывает область карты")
            elif obj.type == OBJECT_DRAGON_LAIR:
                tooltip_lines.append(f"🐉 Опасно! Спавнит дракона")
            elif obj.type == OBJECT_MAGIC_WELL:
                tooltip_lines.append(f"⛲ +3 к атаке и защите")
            
            title_color = arcade.color.YELLOW
        
        # Подсказка для предмета на карте
        elif self.hovered_item:
            item = self.hovered_item
            rarity_colors = {
                "common": arcade.color.WHITE,
                "rare": (100, 100, 255),
                "epic": (200, 100, 255),
                "legendary": (255, 165, 0)
            }
            title_color = rarity_colors.get(item.rarity, arcade.color.WHITE)
            
            tooltip_lines = [f"🎁 {item.name}"]
            
            if item.attack > 0:
                tooltip_lines.append(f"⚔️ Атака: +{item.attack}")
            if item.defense > 0:
                tooltip_lines.append(f"🛡️ Защита: +{item.defense}")
            if item.hp > 0:
                tooltip_lines.append(f"❤️ Здоровье: +{item.hp}")
            
            rarity_names = {"common": "Обычный", "rare": "Редкий", "epic": "Эпический", "legendary": "Легендарный"}
            tooltip_lines.append(f" {rarity_names.get(item.rarity, item.rarity)}")
        
        # Подсказка для врага
        elif self.hovered_enemy:
            enemy = self.hovered_enemy
            names = {
                "wolf": "Волк", "goblin": "Гоблин", "skeleton": "Скелет",
                "lich": "Лич", "golem": "Голем", "dragon": "Дракон",
                "orc": "Орк", "troll": "Тролль", "vampire": "Вампир",
                "demon": "Демон", "bandit": "Бандит", "dark_elf": "Тёмный эльф",
                "giant": "Гигант", "phoenix": "Феникс"
            }
            enemy_name = names.get(enemy.type, "Враг")
            
            tooltip_lines = [
                f"👹 {enemy_name}{enemy.title}",
                f"❤️ HP: {enemy.hp}/{enemy.max_hp}",
                f"⚔️ Атака: {enemy.attack}",
                f"️ Защита: {enemy.defense}",
                f"📅 Неделя спавна: {enemy.spawn_week}"
            ]
            title_color = arcade.color.RED
        
        # Рисуем подсказку если есть
        if tooltip_lines:
            self._render_tooltip(self.mouse_x, self.mouse_y, tooltip_lines, title_color)


    def _render_tooltip(self, x, y, lines, title_color):
        """Рисует подсказку рядом с курсором"""
        if not lines:
            return
        
        # Функция для оценки ширины текста
        def estimate_text_width(text):
            width = 0
            for char in text:
                # Эмодзи и специальные символы шире
                if ord(char) > 0x1F000 or char in '👤❤️⚔️🛡️💰⭐📍🧪📦🍺⛪🏪⛏️🏛️🗿🗼🐉⛲🎁📊👹📅':
                    width += 14
                # Русские буквы и обычные символы
                elif ord(char) > 0x400:
                    width += 7
                else:
                    width += 6
            return width
        
        # Измеряем ширину каждой строки
        line_widths = [estimate_text_width(line) for line in lines]
        
        max_width = max(line_widths) if line_widths else 100
        padding = 12  # Отступы внутри прямоугольника
        total_width = max_width + padding * 2
        line_height = 18
        total_height = len(lines) * line_height + padding * 2
        
        # Позиционируем подсказку рядом с курсором (справа и чуть выше)
        tooltip_x = x + 15
        tooltip_y = y + 10
        
        # Ограничиваем чтобы не выходило за экран
        if tooltip_x + total_width > self.width:
            tooltip_x = x - total_width - 15  # Показываем слева от курсора
        if tooltip_y + total_height > self.height:
            tooltip_y = self.height - total_height - 5
        if tooltip_y < 0:
            tooltip_y = 5
        
        # Рисуем фон
        arcade.draw_lbwh_rectangle_filled(
            tooltip_x, tooltip_y, total_width, total_height,
            (20, 20, 30, 240)
        )
        arcade.draw_lbwh_rectangle_outline(
            tooltip_x, tooltip_y, total_width, total_height,
            (150, 150, 150), 1
        )
        
        # Рисуем текст (начинаем с верхней строки)
        text_y = tooltip_y + total_height - padding - 5
        for i, line in enumerate(lines):
            color = title_color if i == 0 else arcade.color.LIGHT_GRAY
            # Центрируем текст по горизонтали внутри прямоугольника
            text_x = tooltip_x + total_width // 2
            arcade.draw_text(
                line,
                text_x, text_y,
                color, 11,
                anchor_x="center", anchor_y="top",
                font_name="Arial"
            )
            text_y -= line_height

    def is_near_merchant(self):
        """Проверяет есть ли магазин рядом с героем"""
        if not hasattr(self, 'map_objects'):
            return False
        
        for obj in self.map_objects:
            if obj.type == OBJECT_MERCHANT and obj.permanent:
                dist = abs(obj.x - self.hero.x) + abs(obj.y - self.hero.y)
                if dist <= 2:  # В радиусе 2 клеток
                    return True
        return False

    def on_mouse_motion(self, x, y, dx, dy):
        """Отслеживание наведения мыши на объекты"""
        self.mouse_x = x
        self.mouse_y = y
        
        # Сбрасываем все hover
        self.hovered_object = None
        self.hovered_item = None
        self.hovered_enemy = None
        self.hovered_hero = False
        self.hovered_inventory_item = None
        self.hovered_equipment_item = None
        
        # Если открыт инвентарь — проверяем наведение на слоты
        if self.show_inventory:
            self._check_inventory_hover(x, y)
            return
        
        # ВАЖНО: учитываем смещение viewport
        mouse_in_viewport_x = x - CONSOLE_WIDTH
        mouse_in_viewport_y = y - UI_HEIGHT
        
        if mouse_in_viewport_x < 0 or mouse_in_viewport_x > self.game_width:
            return
        if mouse_in_viewport_y < 0 or mouse_in_viewport_y > self.game_height:
            return
        
        # Проверяем героя
        hero_screen_x = self.hero.x * TILE_SIZE - self.camera_x
        hero_screen_y = self.hero.y * TILE_SIZE - self.camera_y
        if (hero_screen_x <= mouse_in_viewport_x <= hero_screen_x + TILE_SIZE and
            hero_screen_y <= mouse_in_viewport_y <= hero_screen_y + TILE_SIZE):
            self.hovered_hero = True
            return
        
        # Проверяем объекты карты
        if hasattr(self, 'map_objects'):
            for obj in self.map_objects:
                if obj.collected and not obj.permanent:
                    continue
                if self.fog[obj.y][obj.x] != 2:
                    continue
                screen_x = obj.x * TILE_SIZE - self.camera_x
                screen_y = obj.y * TILE_SIZE - self.camera_y
                if (screen_x <= mouse_in_viewport_x <= screen_x + TILE_SIZE and
                    screen_y <= mouse_in_viewport_y <= screen_y + TILE_SIZE):
                    self.hovered_object = obj
                    return
        
        # Проверяем предметы экипировки на карте
        if hasattr(self, 'items_on_map'):
            for item in self.items_on_map:
                screen_x = item.x * TILE_SIZE - self.camera_x
                screen_y = item.y * TILE_SIZE - self.camera_y
                if (screen_x <= mouse_in_viewport_x <= screen_x + TILE_SIZE and
                    screen_y <= mouse_in_viewport_y <= screen_y + TILE_SIZE):
                    self.hovered_item = item
                    return
        
        # Проверяем врагов
        for enemy in self.enemies:
            if self.fog[enemy.y][enemy.x] != 2:
                continue
            screen_x = enemy.x * TILE_SIZE - self.camera_x
            screen_y = enemy.y * TILE_SIZE - self.camera_y
            if (screen_x <= mouse_in_viewport_x <= screen_x + TILE_SIZE and
                screen_y <= mouse_in_viewport_y <= screen_y + TILE_SIZE):
                self.hovered_enemy = enemy
                return
    
    def _check_inventory_hover(self, x, y):
        """Проверяет наведение мыши на слоты инвентаря"""
        from inventory_ui import SLOT_SIZE, SLOT_PADDING
        
        panel_width = 900
        panel_height = 600
        cx = self.width / 2
        cy = self.height / 2
        
        panel_left = cx - panel_width / 2
        panel_top = cy + panel_height / 2
        
        # === Проверяем слоты экипировки (левая часть) ===
        left_x = panel_left + 50
        
        # Слот оружия
        slot_y = panel_top - 180
        if self._check_slot_click(x, y, left_x, slot_y, SLOT_SIZE):
            if self.hero.equipped_weapon:
                self.hovered_equipment_item = self.hero.equipped_weapon
            return
        
        # Слот брони
        slot_y -= 130
        if self._check_slot_click(x, y, left_x, slot_y, SLOT_SIZE):
            if self.hero.equipped_armor:
                self.hovered_equipment_item = self.hero.equipped_armor
            return
        
        # Слот аксессуара
        slot_y -= 130
        if self._check_slot_click(x, y, left_x, slot_y, SLOT_SIZE):
            if self.hero.equipped_accessory:
                self.hovered_equipment_item = self.hero.equipped_accessory
            return
        
        # === Проверяем слоты инвентаря (правая часть) ===
        right_x = cx + 150
        inventory_y = panel_top - 100
        slots_per_row = 5
        start_x = right_x
        start_y = inventory_y - 80
        
        for i, item in enumerate(self.hero.inventory):
            row = i // slots_per_row
            col = i % slots_per_row
            
            slot_x = start_x + col * (SLOT_SIZE + SLOT_PADDING)
            slot_y = start_y - row * (SLOT_SIZE + SLOT_PADDING)
            
            if (slot_x - SLOT_SIZE//2 <= x <= slot_x + SLOT_SIZE//2 and
                slot_y - SLOT_SIZE//2 <= y <= slot_y + SLOT_SIZE//2):
                self.hovered_inventory_item = item
                return
            

    def update_camera(self):
        """Смещаем камеру так, чтобы герой был в центре, но не выходил за границы"""
        # Размер карты в пикселях
        map_pixel_width = MAP_WIDTH * TILE_SIZE
        map_pixel_height = MAP_HEIGHT * TILE_SIZE
        
        # Позиция героя в мировых координатах
        hero_world_x = self.hero.x * TILE_SIZE + TILE_SIZE // 2
        hero_world_y = self.hero.y * TILE_SIZE + TILE_SIZE // 2
        
        # Идеальная позиция камеры (герой в центре)
        ideal_camera_x = hero_world_x - self.game_width / 2
        ideal_camera_y = hero_world_y - self.game_height / 2
        
        # ⚠️ ГЛАВНОЕ ИЗМЕНЕНИЕ: добавляем TILE_SIZE к max_x и max_y
        # Это даёт камере запас, чтобы герой на краю карты был полностью виден
        min_x = 0
        max_x = max(0, map_pixel_width - self.game_width + TILE_SIZE)
        min_y = 0
        max_y = max(0, map_pixel_height - self.game_height + TILE_SIZE)
        
        # Применяем ограничения
        self.camera_x = max(min_x, min(ideal_camera_x, max_x))
        self.camera_y = max(min_y, min(ideal_camera_y, max_y))


    def advance_turn(self):
        self.turns += 1
        if self.turns > 0 and self.turns % TURNS_PER_WEEK == 0:
            self.spawn_weekly_resources_and_enemies()
            # Автосохранение каждую неделю
            save_game(self)
            self.log_message("💾 Игра автоматически сохранена!")
        if self.turns >= WEEKS_TO_WIN * TURNS_PER_WEEK:
            self.game_over = True
            self.victory = True
    
    def spawn_weekly_resources_and_enemies(self):
        current_week = (self.turns // TURNS_PER_WEEK) + 1
        self.log_message(f"📅 Неделя {current_week}: Появились новые ресурсы и враги!")
        
        # Генерируем новые квесты
        new_quests = generate_weekly_quests(current_week, self.hero.level)
        self.quests.extend(new_quests)
        
        for quest in new_quests:
            self.log_message(f"📜 Новый квест: {quest.get_description()} | Награда: {quest.get_reward_text()}")
        
        # Обновляем статистику врагов
        for enemy in self.enemies:
            if enemy.spawn_week == 1:
                enemy.spawn_week = current_week
            enemy.update_stats()
        
        # Спавним новые объекты карты
        from map_objects import MapObject, get_random_position
        new_objects = []
        
        # Золото
        for _ in range(GOLD_SPAWN_PER_WEEK):
            x, y = get_random_position(self.game_map, self.hero.x, self.hero.y, self.map_objects + new_objects)
            if x is not None:
                new_objects.append(MapObject(x, y, OBJECT_GOLD))
        
        # Зелья
        for _ in range(POTION_SPAWN_PER_WEEK):
            x, y = get_random_position(self.game_map, self.hero.x, self.hero.y, self.map_objects + new_objects)
            if x is not None:
                new_objects.append(MapObject(x, y, OBJECT_POTION))
        
        # Сундуки
        for _ in range(2):
            x, y = get_random_position(self.game_map, self.hero.x, self.hero.y, self.map_objects + new_objects)
            if x is not None:
                chest = MapObject(x, y, OBJECT_CHEST, value=random.randint(100, 300))
                new_objects.append(chest)
        
        self.map_objects.extend(new_objects)
        
        # Спавн врагов
        for _ in range(ENEMIES_SPAWN_PER_WEEK):
            for attempt in range(200):
                x = random.randint(0, MAP_WIDTH - 1)
                y = random.randint(0, MAP_HEIGHT - 1)
                if (self.game_map[y][x] in (TERRAIN_GRASS, TERRAIN_FOREST, TERRAIN_PATH) and  # ← ДОБАВЬ
                    (x, y) != (self.hero.x, self.hero.y) and
                    not any(e.x == x and e.y == y for e in self.enemies)):
                    roll = random.random()
                    if roll < ENEMY_WOLF_CHANCE:
                        self.enemies.append(Enemy(x, y, "wolf", current_week))
                    elif roll < ENEMY_WOLF_CHANCE + ENEMY_GOBLIN_CHANCE:
                        self.enemies.append(Enemy(x, y, "goblin", current_week))
                    elif roll < ENEMY_WOLF_CHANCE + ENEMY_GOBLIN_CHANCE + ENEMY_SKELETON_CHANCE:
                        self.enemies.append(Enemy(x, y, "skeleton", current_week))
                    elif roll < ENEMY_WOLF_CHANCE + ENEMY_GOBLIN_CHANCE + ENEMY_SKELETON_CHANCE + ENEMY_LICH_CHANCE:
                        self.enemies.append(Enemy(x, y, "lich", current_week))
                    elif roll < ENEMY_WOLF_CHANCE + ENEMY_GOBLIN_CHANCE + ENEMY_SKELETON_CHANCE + ENEMY_LICH_CHANCE + ENEMY_GOLEM_CHANCE:
                        self.enemies.append(Enemy(x, y, "golem", current_week))
                    elif roll < ENEMY_WOLF_CHANCE + ENEMY_GOBLIN_CHANCE + ENEMY_SKELETON_CHANCE + ENEMY_LICH_CHANCE + ENEMY_GOLEM_CHANCE + ENEMY_DRAGON_CHANCE:
                        self.enemies.append(Enemy(x, y, "dragon", current_week))
                    elif roll < ENEMY_WOLF_CHANCE + ENEMY_GOBLIN_CHANCE + ENEMY_SKELETON_CHANCE + ENEMY_LICH_CHANCE + ENEMY_GOLEM_CHANCE + ENEMY_DRAGON_CHANCE + 0.15:
                        self.enemies.append(Enemy(x, y, "orc", current_week))
                    elif roll < ENEMY_WOLF_CHANCE + ENEMY_GOBLIN_CHANCE + ENEMY_SKELETON_CHANCE + ENEMY_LICH_CHANCE + ENEMY_GOLEM_CHANCE + ENEMY_DRAGON_CHANCE + 0.15 + 0.08:
                        self.enemies.append(Enemy(x, y, "troll", current_week))
                    elif roll < ENEMY_WOLF_CHANCE + ENEMY_GOBLIN_CHANCE + ENEMY_SKELETON_CHANCE + ENEMY_LICH_CHANCE + ENEMY_GOLEM_CHANCE + ENEMY_DRAGON_CHANCE + 0.15 + 0.08 + 0.07:
                        self.enemies.append(Enemy(x, y, "vampire", current_week))
                    elif roll < ENEMY_WOLF_CHANCE + ENEMY_GOBLIN_CHANCE + ENEMY_SKELETON_CHANCE + ENEMY_LICH_CHANCE + ENEMY_GOLEM_CHANCE + ENEMY_DRAGON_CHANCE + 0.15 + 0.08 + 0.07 + 0.05:
                        self.enemies.append(Enemy(x, y, "demon", current_week))
                    elif roll < ENEMY_WOLF_CHANCE + ENEMY_GOBLIN_CHANCE + ENEMY_SKELETON_CHANCE + ENEMY_LICH_CHANCE + ENEMY_GOLEM_CHANCE + ENEMY_DRAGON_CHANCE + 0.15 + 0.08 + 0.07 + 0.05 + 0.12:
                        self.enemies.append(Enemy(x, y, "bandit", current_week))
                    elif roll < ENEMY_WOLF_CHANCE + ENEMY_GOBLIN_CHANCE + ENEMY_SKELETON_CHANCE + ENEMY_LICH_CHANCE + ENEMY_GOLEM_CHANCE + ENEMY_DRAGON_CHANCE + 0.15 + 0.08 + 0.07 + 0.05 + 0.12 + 0.06:
                        self.enemies.append(Enemy(x, y, "dark_elf", current_week))
                    elif roll < ENEMY_WOLF_CHANCE + ENEMY_GOBLIN_CHANCE + ENEMY_SKELETON_CHANCE + ENEMY_LICH_CHANCE + ENEMY_GOLEM_CHANCE + ENEMY_DRAGON_CHANCE + 0.15 + 0.08 + 0.07 + 0.05 + 0.12 + 0.06 + 0.04:
                        self.enemies.append(Enemy(x, y, "giant", current_week))
                    else:
                        self.enemies.append(Enemy(x, y, "phoenix", current_week))
                    break

    def update_fog(self):
        FOG_RADIUS = 2
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                dist_x = abs(x - self.hero.x)
                dist_y = abs(y - self.hero.y)
                if dist_x <= FOG_RADIUS and dist_y <= FOG_RADIUS:
                    self.fog[y][x] = 2
                elif self.fog[y][x] == 2:
                    self.fog[y][x] = 1
    

    def generate_enemies(self):
        enemies = []
        def add_enemy(enemy_type, count):
            for _ in range(count):
                for attempt in range(200):
                    x = random.randint(0, MAP_WIDTH - 1)
                    y = random.randint(0, MAP_HEIGHT - 1)
                    if (self.game_map[y][x] in (TERRAIN_GRASS, TERRAIN_FOREST) and 
                        (x, y) != (self.hero.x, self.hero.y) and
                        not any(e.x == x and e.y == y for e in enemies)):
                        enemies.append(Enemy(x, y, enemy_type, spawn_week=1))
                        break
        add_enemy("wolf", ENEMY_WOLF_COUNT)
        add_enemy("goblin", ENEMY_GOBLIN_COUNT)
        add_enemy("skeleton", ENEMY_SKELETON_COUNT)
        add_enemy("lich", ENEMY_LICH_COUNT)
        add_enemy("golem", ENEMY_GOLEM_COUNT)
        add_enemy("dragon", ENEMY_DRAGON_COUNT)
        add_enemy("orc", 4)
        add_enemy("troll", 2)
        add_enemy("vampire", 2)
        add_enemy("demon", 1)
        add_enemy("bandit", 3)
        add_enemy("dark_elf", 2)
        add_enemy("giant", 1)
        add_enemy("phoenix", 1)
        return enemies
    
    def update_enemies(self):
        for enemy in self.enemies:
            dist = abs(enemy.x - self.hero.x) + abs(enemy.y - self.hero.y)
            if dist <= 1:
                enemy.is_aggroed = True
            if enemy.is_aggroed:
                if dist > 5:
                    enemy.is_aggroed = False
                else:
                    dx = self.hero.x - enemy.x
                    dy = self.hero.y - enemy.y
                    move_x = 1 if dx > 0 else -1 if dx < 0 else 0
                    move_y = 1 if dy > 0 else -1 if dy < 0 else 0
                    if abs(dx) > abs(dy):
                        new_x, new_y = enemy.x + move_x, enemy.y
                    else:
                        new_x, new_y = enemy.x, enemy.y + move_y
                    if new_x == self.hero.x and new_y == self.hero.y:
                        damage = self.hero.take_damage(enemy.attack)
                        self.log_message(f"⚔️ {enemy.emoji} атакует вас! Урон: {damage}")
                        if not self.hero.is_alive():
                            self.game_over = True
                            self.victory = False
                    else:
                        if self.game_map[new_y][new_x] in (TERRAIN_GRASS, TERRAIN_FOREST, TERRAIN_PATH):
                            is_blocked = any(e.x == new_x and e.y == new_y for e in self.enemies if e != enemy)
                            if not is_blocked:
                                enemy.x = new_x
                                enemy.y = new_y
    
    def draw_terrain_tile(self, x, y, terrain_type, screen_x, screen_y):
        """Рисует клетку местности с текстурами"""
        # Определяем какую текстуру использовать (псевдослучайно по координатам)
        texture_list = None
        
        if terrain_type == TERRAIN_GRASS:
            texture_list = self.terrain_textures.get('grass', [])
        elif terrain_type == TERRAIN_FOREST:
            texture_list = self.terrain_textures.get('forest', [])
        elif terrain_type == TERRAIN_WATER:
            texture_list = self.terrain_textures.get('water', [])
        elif terrain_type == TERRAIN_MOUNTAIN:
            texture_list = self.terrain_textures.get('mountain', [])
        elif terrain_type == TERRAIN_PATH:
            texture_list = self.terrain_textures.get('path', [])
        
        # Рисуем текстуру если есть
        if texture_list:
            # Выбираем текстуру на основе координат (для разнообразия)
            index = (x * 7 + y * 13) % len(texture_list)
            texture = texture_list[index]
            
            center_x = screen_x + TILE_SIZE // 2
            center_y = screen_y + TILE_SIZE // 2
            rect = arcade.XYWH(center_x, center_y, TILE_SIZE, TILE_SIZE)
            arcade.draw_texture_rect(texture, rect)
        else:
            # Fallback на цветные квадраты (если нет текстур)
            self._draw_fallback_tile(x, y, terrain_type, screen_x, screen_y)
    
    def _draw_fallback_tile(self, x, y, terrain_type, screen_x, screen_y):
        """Рисует клетку без текстур (процедурно)"""
        if terrain_type == TERRAIN_GRASS:
            arcade.draw_lbwh_rectangle_filled(screen_x, screen_y, TILE_SIZE, TILE_SIZE, COLOR_GRASS)
            # Травинки
            seed = x * 1000 + y
            random.seed(seed)
            for _ in range(3):
                gx = screen_x + random.randint(5, 59)
                gy = screen_y + random.randint(5, 59)
                arcade.draw_line(gx, gy, gx + random.randint(-2, 2), gy + random.randint(4, 8), (50, 150, 50), 2)
            random.seed()
        elif terrain_type == TERRAIN_PATH:
            arcade.draw_lbwh_rectangle_filled(screen_x, screen_y, TILE_SIZE, TILE_SIZE, (180, 160, 120))
            seed = x * 1000 + y
            random.seed(seed)
            for _ in range(2):
                sx = screen_x + random.randint(10, 54)
                sy = screen_y + random.randint(10, 54)
                arcade.draw_circle_filled(sx, sy, random.randint(2, 4), (160, 140, 100))
            random.seed()
        elif terrain_type == TERRAIN_MOUNTAIN:
            arcade.draw_lbwh_rectangle_filled(screen_x, screen_y, TILE_SIZE, TILE_SIZE, COLOR_MOUNTAIN)
            points = [(screen_x + TILE_SIZE//2, screen_y + TILE_SIZE - 10),
                      (screen_x + 10, screen_y + 20),
                      (screen_x + TILE_SIZE - 10, screen_y + 20)]
            arcade.draw_polygon_filled(points, COLOR_MOUNTAIN_PEAK)
        elif terrain_type == TERRAIN_WATER:
            arcade.draw_lbwh_rectangle_filled(screen_x, screen_y, TILE_SIZE, TILE_SIZE, COLOR_WATER)
            arcade.draw_arc_outline(screen_x + 16, screen_y + 20, 20, 10, COLOR_WATER_WAVE, 0, 180, 2)
        elif terrain_type == TERRAIN_FOREST:
            arcade.draw_lbwh_rectangle_filled(screen_x, screen_y, TILE_SIZE, TILE_SIZE, COLOR_FOREST)
    
    def _draw_fallback_tile(self, x, y, terrain_type, screen_x, screen_y):
        """Рисует клетку без текстур (процедурно)"""
        if terrain_type == TERRAIN_GRASS:
            arcade.draw_lbwh_rectangle_filled(screen_x, screen_y, TILE_SIZE, TILE_SIZE, COLOR_GRASS)
            # Травинки
            seed = x * 1000 + y
            random.seed(seed)
            for _ in range(3):
                gx = screen_x + random.randint(5, 59)
                gy = screen_y + random.randint(5, 59)
                arcade.draw_line(gx, gy, gx + random.randint(-2, 2), gy + random.randint(4, 8), (50, 150, 50), 2)
            random.seed()
        elif terrain_type == TERRAIN_PATH:
            arcade.draw_lbwh_rectangle_filled(screen_x, screen_y, TILE_SIZE, TILE_SIZE, (180, 160, 120))
            seed = x * 1000 + y
            random.seed(seed)
            for _ in range(2):
                sx = screen_x + random.randint(10, 54)
                sy = screen_y + random.randint(10, 54)
                arcade.draw_circle_filled(sx, sy, random.randint(2, 4), (160, 140, 100))
            random.seed()
        elif terrain_type == TERRAIN_MOUNTAIN:
            arcade.draw_lbwh_rectangle_filled(screen_x, screen_y, TILE_SIZE, TILE_SIZE, COLOR_MOUNTAIN)
            points = [(screen_x + TILE_SIZE//2, screen_y + TILE_SIZE - 10),
                      (screen_x + 10, screen_y + 20),
                      (screen_x + TILE_SIZE - 10, screen_y + 20)]
            arcade.draw_polygon_filled(points, COLOR_MOUNTAIN_PEAK)
        elif terrain_type == TERRAIN_WATER:
            arcade.draw_lbwh_rectangle_filled(screen_x, screen_y, TILE_SIZE, TILE_SIZE, COLOR_WATER)
            arcade.draw_arc_outline(screen_x + 16, screen_y + 20, 20, 10, COLOR_WATER_WAVE, 0, 180, 2)
        elif terrain_type == TERRAIN_FOREST:
            arcade.draw_lbwh_rectangle_filled(screen_x, screen_y, TILE_SIZE, TILE_SIZE, COLOR_FOREST)
    

    def on_draw(self):
        self.clear()
        
        self.ctx.viewport = (CONSOLE_WIDTH, UI_HEIGHT, self.game_width, self.game_height)
        
        # Отрисовка карты
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                world_x = x * TILE_SIZE
                world_y = y * TILE_SIZE
                
                screen_x = world_x - self.camera_x
                screen_y = world_y - self.camera_y
                
                if screen_x < -TILE_SIZE or screen_x > self.game_width + TILE_SIZE:
                    continue
                if screen_y < -TILE_SIZE or screen_y > self.game_height + TILE_SIZE:
                    continue       
                
                fog_state = self.fog[y][x]
                
                if fog_state == 0:
                    arcade.draw_lbwh_rectangle_filled(screen_x, screen_y, TILE_SIZE, TILE_SIZE, (0, 0, 0))
                    continue
                
                self.draw_terrain_tile(x, y, self.game_map[y][x], screen_x, screen_y)
                arcade.draw_lbwh_rectangle_outline(screen_x, screen_y, TILE_SIZE, TILE_SIZE, COLOR_GRID, 1)
                
                if fog_state == 1:
                    arcade.draw_lbwh_rectangle_filled(screen_x, screen_y, TILE_SIZE, TILE_SIZE, (0, 0, 0, 160))
                    if self.game_map[y][x] == TERRAIN_FOREST:
                        arcade.draw_text("🌲", screen_x + TILE_SIZE//2, screen_y + TILE_SIZE//2, 
                                         (255, 255, 255, 100), 32, anchor_x="center", anchor_y="center")
        
        # 🏰 ОТРИСОВКА ОБЪЕКТОВ КАРТЫ
        if hasattr(self, 'map_objects'):
            for obj in self.map_objects:
                if not obj.collected and self.fog[obj.y][obj.x] == 2:
                    screen_x = obj.x * TILE_SIZE - self.camera_x
                    screen_y = obj.y * TILE_SIZE - self.camera_y
                    obj.draw(screen_x, screen_y)
        
        # 🎁 ПРЕДМЕТЫ ЭКИПИРОВКИ НА КАРТЕ
        if hasattr(self, 'items_on_map'):
            for item in self.items_on_map:
                if self.fog[item.y][item.x] == 2:
                    screen_x = item.x * TILE_SIZE - self.camera_x
                    screen_y = item.y * TILE_SIZE - self.camera_y
                    color = item.get_color()
                    
                    if item.type == "weapon":
                        icon = "⚔️"
                    elif item.type == "armor":
                        icon = "🛡️"
                    elif item.type == "accessory":
                        icon = "💍"
                    else:
                        icon = "📦"
                    
                    arcade.draw_text(icon, screen_x + TILE_SIZE//2 + 2, screen_y + TILE_SIZE//2 - 2, (0,0,0,100), 28, anchor_x="center", anchor_y="center")
                    arcade.draw_text(icon, screen_x + TILE_SIZE//2, screen_y + TILE_SIZE//2, color, 28, anchor_x="center", anchor_y="center")
        
        # Враги
        for enemy in self.enemies:
            if self.fog[enemy.y][enemy.x] == 2:
                screen_x = enemy.x * TILE_SIZE - self.camera_x
                screen_y = enemy.y * TILE_SIZE - self.camera_y
                enemy.draw(screen_x, screen_y)
        
        # Герой
        hero_screen_x = self.hero.x * TILE_SIZE - self.camera_x
        hero_screen_y = self.hero.y * TILE_SIZE - self.camera_y
        self.hero.draw(hero_screen_x, hero_screen_y)
        self.combat_animator.draw()
        
        # ==========================================
        # UI (сбрасываем viewport)
        # ==========================================
        self.ctx.viewport = (0, 0, self.width, self.height)
        
        arcade.draw_text("📜 ЖУРНАЛ СОБЫТИЙ", 15, self.height - 40, arcade.color.GOLD, 14, font_name="Arial", bold=True)
        arcade.draw_line(10, self.height - 55, CONSOLE_WIDTH - 15, self.height - 55, (100, 100, 100), 1)
        
        y_offset = self.height - 80
        for i, msg in enumerate(reversed(self.messages)):
            display_msg = msg[:45] + ("..." if len(msg) > 45 else "")
            arcade.draw_text(display_msg, 15, y_offset - (i * 20), arcade.color.LIGHT_GRAY, 12, font_name="Arial")
        
        ui_center_x = CONSOLE_WIDTH + self.game_width / 2
        ui_center_y = UI_HEIGHT / 2
        
        current_day = (self.turns // TURNS_PER_DAY) + 1
        current_week = (self.turns // TURNS_PER_WEEK) + 1
        
        if not self.shop_mode:
            arcade.draw_text(f"📅 Неделя: {current_week}, День: {current_day} | Ход: {self.turns}", 
                             CONSOLE_WIDTH + 15, 50, arcade.color.WHITE, 13, font_name="Arial", bold=True)
            arcade.draw_text(f"Ур: {self.hero.level} | 💰: {self.hero.gold} | ❤️: {self.hero.hp}/{self.hero.max_hp}", 
                             ui_center_x, 30, arcade.color.WHITE, 13, font_name="Arial", anchor_x="center")
            arcade.draw_text(f"⚔️: {self.hero.attack} | 🛡️: {self.hero.defense} | 👹: {len(self.enemies)} | [M] Магазин", 
                             self.width - 380, 30, arcade.color.LIGHT_GRAY, 12, font_name="Arial")
            
            arcade.draw_text("[H] Подсказки | [I] Инвентарь", 
                             self.width - 20, 50, (100, 200, 255), 11, 
                             font_name="Arial", anchor_x="right")
        else:
            arcade.draw_text(f"🏰 МАГАЗИН | 💰: {self.hero.gold}", ui_center_x, 50, arcade.color.GOLD, 14, font_name="Arial", bold=True, anchor_x="center")
            
            attack_cost = UPGRADE_ATTACK_COST + (self.hero.attack_upgrades * 150)
            defense_cost = UPGRADE_DEFENSE_COST + (self.hero.defense_upgrades * 150)
            hp_cost = UPGRADE_HP_COST + (self.hero.hp_upgrades * 200)
            
            attack_text = f"[1] Атака +{UPGRADE_AMOUNT} ({attack_cost}g)" if self.hero.attack < MAX_ATTACK else "[1] МАКС"
            defense_text = f"[2] Защита +{UPGRADE_AMOUNT} ({defense_cost}g)" if self.hero.defense < MAX_DEFENSE else "[2] МАКС"
            hp_text = f"[3] HP +{UPGRADE_AMOUNT*2} ({hp_cost}g)" if self.hero.max_hp < MAX_HP else "[3] МАКС"
            
            # Показываем предметы для продажи
            sell_info = " | [4-9] Продать предмет"
            if self.hero.inventory:
                sell_info += f" ({len(self.hero.inventory)} предм.)"
            
            arcade.draw_text(f"{attack_text} | {defense_text} | {hp_text}{sell_info} | [ESC] Закрыть", 
                             ui_center_x, 30, arcade.color.LIGHT_GRAY, 11, font_name="Arial", anchor_x="center")
        
        if self.level_up_timer > 0:
            arcade.draw_text(f"🎉 Уровень повышен! Теперь вы {self.hero.level} уровня!", ui_center_x, self.height / 2 + 50, arcade.color.GOLD, 32, anchor_x="center", font_name="Arial", bold=True)
            self.level_up_timer -= 1
        
        if self.quests:
            arcade.draw_line(10, 180, CONSOLE_WIDTH - 15, 180, (100, 100, 100), 1)
            arcade.draw_text("📋 АКТИВНЫЕ КВЕСТЫ:", 15, 165, arcade.color.GOLD, 12, font_name="Arial", bold=True)
            
            y_quest = 145
            for i, quest in enumerate(self.quests[:3]):
                arcade.draw_text(quest.get_description(), 15, y_quest, arcade.color.LIGHT_GRAY, 10, font_name="Arial")
                arcade.draw_text(quest.get_progress_text(), CONSOLE_WIDTH - 60, y_quest, arcade.color.YELLOW, 10, font_name="Arial", anchor_x="right")
                y_quest -= 25
        
        if self.game_over:
            if self.victory:
                msg = f"🏆 ПОБЕДА! Вы успешно правили {WEEKS_TO_WIN} недель!"
                color = arcade.color.GREEN
            else:
                msg = f"💀 ПОРАЖЕНИЕ! Герой пал в бою..."
                color = arcade.color.RED
            arcade.draw_text(msg, ui_center_x, self.height / 2, color, 28, anchor_x="center", font_name="Arial", bold=True)
            arcade.draw_text("Нажмите R для новой игры", ui_center_x, self.height / 2 - 40, arcade.color.WHITE, 18, anchor_x="center", font_name="Arial")

        if self.show_controls:
            draw_controls_panel()
        
        if self.show_inventory:
            draw_inventory(self)

        # ==========================================
        # ПОДСКАЗКИ ПРИ НАВЕДЕНИИ (ТОЛЬКО ОДИН РАЗ В КОНЦЕ!)
        # ==========================================
        self._draw_hover_tooltips()

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.F1, arcade.key.H):
            self.show_controls = not self.show_controls
            return
        
        # Если подсказки открыты — игнорируем другие клавиши (кроме F1/H)
        if self.show_controls and key not in (arcade.key.F1, arcade.key.H):
            return
        if self.game_over and key == arcade.key.R:
            self.reset_game()
            return
        if self.game_over: return
        
        if self.shop_mode:
            if key == arcade.key.ESCAPE: 
                self.shop_mode = False
            elif key == arcade.key.KEY_1 and self.hero.upgrade_attack(): 
                self.log_message(f"⚔️ Атака улучшена! Теперь: {self.hero.attack}")
            elif key == arcade.key.KEY_2 and self.hero.upgrade_defense(): 
                self.log_message(f"🛡️ Защита улучшена! Теперь: {self.hero.defense}")
            elif key == arcade.key.KEY_3 and self.hero.upgrade_hp(): 
                self.log_message(f"❤️ Здоровье улучшено! Теперь: {self.hero.max_hp}")
            return
        
        if key == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)
            return

        # Магазин открывается только рядом с магазином (клавиша M)
        if key == arcade.key.M:
            # Проверяем есть ли магазин рядом
            merchant_nearby = False
            if hasattr(self, 'map_objects'):
                for obj in self.map_objects:
                    if obj.type == OBJECT_MERCHANT and obj.permanent:
                        dist = abs(obj.x - self.hero.x) + abs(obj.y - self.hero.y)
                        if dist <= 1:
                            merchant_nearby = True
                            break
            
            if merchant_nearby:
                self.shop_mode = True
                self.log_message(" Магазин открыт!")
            else:
                self.log_message("❌ Рядом нет магазина! Найдите здание торговца.")
            return
        
        # Сохранение (F5)
        if key == arcade.key.F5:
            if save_game(self):
                self.log_message("💾 Игра сохранена!")
            return
        
        # Загрузка (F9)
        if key == arcade.key.F9:
            if load_game(self):
                self.log_message("📂 Игра загружена!")
            return
        
        # Инвентарь (I)
        if key == arcade.key.I:
            self.show_inventory = not self.show_inventory
            return
        
        # Если инвентарь открыт — игнорируем другие клавиши
        if self.show_inventory:
            if key == arcade.key.ESCAPE:
                self.show_inventory = False
            elif key in range(arcade.key.KEY_1, arcade.key.KEY_0 + 1):
                # Цифры 1-9 для быстрой экипировки
                slot = key - arcade.key.KEY_1
                if slot < len(self.hero.inventory):
                    success, msg = self.hero.equip_item(slot)
                    self.log_message(msg)
            return

        if self.shop_mode:
            if key == arcade.key.ESCAPE: 
                self.shop_mode = False
            
            # Продажа предметов (клавиши 4-9 для предметов 1-6 в инвентаре)
            elif key in range(arcade.key.KEY_4, arcade.key.KEY_9 + 1):
                slot = key - arcade.key.KEY_4  # 0-5
                if slot < len(self.hero.inventory):
                    item = self.hero.inventory[slot]
                    sell_price = self._get_item_sell_price(item)
                    self.hero.gold += sell_price
                    self.hero.inventory.pop(slot)
                    self.log_message(f"💰 Продано: {item.name} за {sell_price} золота")
            
            elif key == arcade.key.KEY_1 and self.hero.upgrade_attack(): 
                self.log_message(f"⚔️ Атака улучшена! Теперь: {self.hero.attack}")
            elif key == arcade.key.KEY_2 and self.hero.upgrade_defense(): 
                self.log_message(f"🛡️ Защита улучшена! Теперь: {self.hero.defense}")
            elif key == arcade.key.KEY_3 and self.hero.upgrade_hp(): 
                self.log_message(f"❤️ Здоровье улучшено! Теперь: {self.hero.max_hp}")
            return
        
        new_x, new_y = self.hero.x, self.hero.y
        if key in (arcade.key.W, arcade.key.UP) and self.hero.y < MAP_HEIGHT - 1: new_y += 1
        elif key in (arcade.key.S, arcade.key.DOWN) and self.hero.y > 0: new_y -= 1
        elif key in (arcade.key.A, arcade.key.LEFT) and self.hero.x > 0: new_x -= 1
        elif key in (arcade.key.D, arcade.key.RIGHT) and self.hero.x < MAP_WIDTH - 1: new_x += 1

        new_x = max(0, min(new_x, MAP_WIDTH - 1))
        new_y = max(0, min(new_y, MAP_HEIGHT - 1))
        
        action_taken = False
        
        if self.game_map[new_y][new_x] in (TERRAIN_GRASS, TERRAIN_FOREST, TERRAIN_PATH):
            enemy_on_cell = next((e for e in self.enemies if e.x == new_x and e.y == new_y), None)
            if enemy_on_cell:
                self.combat(enemy_on_cell)
                action_taken = True
            else:
                self.hero.x = new_x
                self.hero.y = new_y
                action_taken = True
                
                # 🏰 ОБРАБОТКА ОБЪЕКТОВ КАРТЫ (вместо золота и зелий)
                if hasattr(self, 'map_objects'):
                    obj_on_cell = next((obj for obj in self.map_objects 
                                       if obj.x == self.hero.x and obj.y == self.hero.y and not obj.collected), None)
                    if obj_on_cell:
                        self.handle_object_interaction(obj_on_cell)
                
                # 🎁 Сбор предметов экипировки (ТОЛЬКО после движения)
                if hasattr(self, 'items_on_map'):
                    item_on_cell = next((item for item in self.items_on_map 
                                        if item.x == self.hero.x and item.y == self.hero.y), None)
                    if item_on_cell:
                        success, msg = self.hero.add_to_inventory(item_on_cell)
                        self.log_message(msg)
                        if success:
                            self.items_on_map.remove(item_on_cell)
        
        if action_taken:
            # Отслеживаем исследование новых клеток
            if self.fog[self.hero.y][self.hero.x] == 2:
                self.update_quest_progress("move")
            
            self.advance_turn()
            self.update_fog()
            self.update_enemies()
            self.update_camera()
    

    def combat(self, enemy):
        """Начать анимированный бой"""
        # Позиции ОТНОСИТЕЛЬНО viewport (без CONSOLE_WIDTH и UI_HEIGHT!)
        hero_screen_x = self.hero.x * TILE_SIZE - self.camera_x
        hero_screen_y = self.hero.y * TILE_SIZE - self.camera_y
        enemy_screen_x = enemy.x * TILE_SIZE - self.camera_x
        enemy_screen_y = enemy.y * TILE_SIZE - self.camera_y
        
        # --- Анимация атаки героя ---
        self.combat_animator.add_shake(intensity=8, duration=15)
        
        damage_to_enemy = enemy.take_damage(self.hero.attack)
        
        # Вспышка на враге (правильные координаты)
        self.combat_animator.add_flash(
            enemy_screen_x + TILE_SIZE // 2,
            enemy_screen_y + TILE_SIZE // 2,
            radius=50
        )
        
        # Летящее число урона
        self.combat_animator.add_damage(
            enemy_screen_x + TILE_SIZE // 2,
            enemy_screen_y + TILE_SIZE + 20,
            damage_to_enemy
        )
        
        if not enemy.is_alive():
            self.enemies.remove(enemy)
            self.log_message(f"🏆 Вы победили {enemy.emoji} и получили {XP_PER_KILL} XP!")
            
            if enemy.type not in self.enemies_killed_by_type:
                self.enemies_killed_by_type[enemy.type] = 0
            self.enemies_killed_by_type[enemy.type] += 1
            
            self.update_quest_progress("kill", enemy_type=enemy.type)
            
            if self.hero.gain_xp(XP_PER_KILL):
                self.level_up_timer = 120
                self.log_message(f"🎉 Уровень повышен! Теперь вы {self.hero.level} уровня!")
            
            self.combat_animator.add_flash(
                enemy_screen_x + TILE_SIZE // 2,
                enemy_screen_y + TILE_SIZE // 2,
                radius=80
            )
        else:
            damage_to_hero = self.hero.take_damage(enemy.attack)
            
            self.combat_animator.add_shake(intensity=12, duration=20)
            
            self.combat_animator.add_flash(
                hero_screen_x + TILE_SIZE // 2,
                hero_screen_y + TILE_SIZE // 2,
                radius=50
            )
            
            self.combat_animator.add_damage(
                hero_screen_x + TILE_SIZE // 2,
                hero_screen_y + TILE_SIZE + 20,
                damage_to_hero
            )
            
            self.log_message(f"️ {enemy.emoji} атакует вас! Урон: {damage_to_hero}")
            
            if not self.hero.is_alive():
                self.game_over = True
                self.victory = False
                self.combat_animator.add_flash(
                    hero_screen_x + TILE_SIZE // 2,
                    hero_screen_y + TILE_SIZE // 2,
                    radius=100
                )
        
        self.update_fog()
        self.update_enemies()
        self.update_camera()


    def update_quest_progress(self, event_type, **kwargs):
        """Обновляет прогресс квестов"""
        for quest in self.quests:
            if quest.completed:
                continue
            
            completed_now = False
            
            if quest.type == QUEST_KILL_ENEMIES and event_type == "kill":
                enemy_type = kwargs.get("enemy_type")
                if enemy_type == quest.target:
                    completed_now = quest.add_progress()
            
            elif quest.type == QUEST_COLLECT_GOLD and event_type == "gold":
                amount = kwargs.get("amount", 0)
                # Добавляем к текущему прогрессу квеста
                completed_now = quest.add_progress(amount)
            
            elif quest.type == QUEST_COLLECT_POTIONS and event_type == "potion":
                completed_now = quest.add_progress()
            
            elif quest.type == QUEST_EXPLORE_TILES and event_type == "move":
                completed_now = quest.add_progress()
            
            if completed_now:
                self.log_message(f"✅ Квест выполнен: {quest.get_description()}")
                self.log_message(f"🎁 Награда: {quest.get_reward_text()}")
                
                # Выдаём награду
                self.hero.gold += quest.reward_gold
                if quest.reward_xp > 0:
                    if self.hero.gain_xp(quest.reward_xp):
                        self.level_up_timer = 120
                        self.log_message(f"🎉 Уровень повышен! Теперь вы {self.hero.level} уровня!")
                
                self.completed_quests.append(quest)
        
        # Удаляем выполненные квесты из активных
        self.quests = [q for q in self.quests if not q.completed]


    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка клика мыши"""
        
        # ПРАВЫЙ КЛИК - продажа предмета в инвентаре
        if button == arcade.MOUSE_BUTTON_RIGHT and self.show_inventory:
            # Проверяем есть ли магазин рядом
            if not self.is_near_merchant():
                self.log_message("❌ Рядом нет магазина! Найдите здание торговца для продажи.")
                return
            
            from inventory_ui import SLOT_SIZE, SLOT_PADDING
            
            panel_width = 900
            panel_height = 600
            cx = self.width / 2
            cy = self.height / 2
            
            panel_left = cx - panel_width / 2
            panel_top = cy + panel_height / 2
            
            # Проверяем слоты инвентаря (правая часть)
            right_x = cx + 150
            inventory_y = panel_top - 100
            slots_per_row = 5
            start_x = right_x
            start_y = inventory_y - 80
            
            for i, item in enumerate(self.hero.inventory):
                row = i // slots_per_row
                col = i % slots_per_row
                
                slot_x = start_x + col * (SLOT_SIZE + SLOT_PADDING)
                slot_y = start_y - row * (SLOT_SIZE + SLOT_PADDING)
                
                if (slot_x - SLOT_SIZE//2 <= x <= slot_x + SLOT_SIZE//2 and
                    slot_y - SLOT_SIZE//2 <= y <= slot_y + SLOT_SIZE//2):
                    
                    # Продаём предмет
                    sell_price = self._get_item_sell_price(item)
                    self.hero.gold += sell_price
                    self.hero.inventory.pop(i)
                    self.log_message(f"💰 Продано: {item.name} за {sell_price} золота")
                    return
            
            return
        
       
        if not self.show_inventory:
            return
        
        from inventory_ui import SLOT_PADDING, SLOT_SIZE

        # Координаты панели (должны совпадать с draw_inventory)
        panel_width = 900
        panel_height = 600
        cx = self.width / 2
        cy = self.height / 2
        
        left = cx - panel_width / 2
        right = cx + panel_width / 2
        top = cy + panel_height / 2
        bottom = cy - panel_height / 2
        
        # === ПРОВЕРКА КЛИКА ПО ИНВЕНТАРЮ (правая часть) ===
        right_x = cx + 100
        inventory_y = top - 100
        slots_per_row = 5
        start_x = right_x
        start_y = inventory_y - 80
        
        for i, item in enumerate(self.hero.inventory):
            row = i // slots_per_row
            col = i % slots_per_row
            
            slot_x = start_x + col * (SLOT_SIZE + SLOT_PADDING)
            slot_y = start_y - row * (SLOT_SIZE + SLOT_PADDING)
            
            # Проверяем попадает ли клик в слот
            if (slot_x - SLOT_SIZE//2 <= x <= slot_x + SLOT_SIZE//2 and
                slot_y - SLOT_SIZE//2 <= y <= slot_y + SLOT_SIZE//2):
                
                # Экипируем предмет
                success, msg = self.hero.equip_item(i)
                self.log_message(msg)
                return
        
        # === ПРОВЕРКА КЛИКА ПО СЛОТАМ ЭКИПИРОВКИ (левая часть) ===
        left_x = left + 100
        
        # Слот оружия
        slot_y = top - 180
        if self._check_slot_click(x, y, left_x, slot_y, SLOT_SIZE):
            if self.hero.equipped_weapon:
                success, msg = self.hero.unequip_item("weapon")
                self.log_message(msg)
            return
        
        # Слот брони
        slot_y -= 130
        if self._check_slot_click(x, y, left_x, slot_y, SLOT_SIZE):
            if self.hero.equipped_armor:
                success, msg = self.hero.unequip_item("armor")
                self.log_message(msg)
            return
        
        # Слот аксессуара
        slot_y -= 130
        if self._check_slot_click(x, y, left_x, slot_y, SLOT_SIZE):
            if self.hero.equipped_accessory:
                success, msg = self.hero.unequip_item("accessory")
                self.log_message(msg)
            return
    
    def _check_slot_click(self, mouse_x, mouse_y, slot_x, slot_y, slot_size):
        """Проверяет попал ли клик в слот"""
        return (slot_x - slot_size//2 <= mouse_x <= slot_x + slot_size//2 and
                slot_y - slot_size//2 <= mouse_y <= slot_y + slot_size//2)
    

    def handle_object_interaction(self, obj):
        """Обрабатывает взаимодействие с объектом на карте"""
        from map_objects import (OBJECT_GOLD, OBJECT_POTION, OBJECT_CHEST, OBJECT_MINE,
                                OBJECT_TAVERN, OBJECT_TEMPLE, OBJECT_RUINS, OBJECT_SHRINE,
                                OBJECT_DRAGON_LAIR, OBJECT_WATCHTOWER, OBJECT_MERCHANT,
                                OBJECT_MAGIC_WELL)
        
        if obj.type == OBJECT_GOLD:
            self.hero.gold += GOLD_PER_PILE
            self.log_message(f"💰 Вы нашли {GOLD_PER_PILE} золота!")
            self.update_quest_progress("gold", amount=GOLD_PER_PILE)
            if not obj.permanent:
                obj.collected = True
        
        elif obj.type == OBJECT_POTION:
            heal_amount = 40
            self.hero.heal(heal_amount)
            self.log_message(f"🧪 Вы выпили зелье! HP: {self.hero.hp}/{self.hero.max_hp}")
            self.update_quest_progress("potion")
            if not obj.permanent:
                obj.collected = True
        
        elif obj.type == OBJECT_CHEST:
            gold_amount = obj.value
            self.hero.gold += gold_amount
            self.log_message(f"📦 Вы открыли сундук и нашли {gold_amount} золота!")
            self.update_quest_progress("gold", amount=gold_amount)
            if not obj.permanent:
                obj.collected = True
        
        elif obj.type == OBJECT_MINE:
            gold_amount = 50
            self.hero.gold += gold_amount
            self.log_message(f"⛏️ Вы добыли {gold_amount} золота из шахты!")
            self.update_quest_progress("gold", amount=gold_amount)
            if not obj.permanent:
                obj.collected = True
        
        elif obj.type == OBJECT_TAVERN:
            if self.hero.hp >= self.hero.max_hp:
                self.log_message(" Вы полностью здоровы!")
            else:
                self.hero.hp = self.hero.max_hp
                self.log_message("🍺 Вы отдохнули в таверне и полностью восстановили здоровье!")
            # НЕ помечаем как collected - permanent=True
        
        elif obj.type == OBJECT_TEMPLE:
            if self.hero.hp >= self.hero.max_hp:
                self.log_message("⛪ Вы полностью здоровы!")
            else:
                self.hero.hp = self.hero.max_hp
                self.log_message("⛪ Храм благословил вас! Здоровье полностью восстановлено!")
            # НЕ помечаем как collected - permanent=True
        
        elif obj.type == OBJECT_RUINS:
            if random.random() < 0.7:
                from items import generate_random_item
                item = generate_random_item(min_week=2)
                success, msg = self.hero.add_to_inventory(item)
                if success:
                    self.log_message(f"️ В руинах вы нашли: {item.name}!")
                else:
                    self.log_message(f"🏛️ {msg}")
            else:
                gold_amount = random.randint(50, 150)
                self.hero.gold += gold_amount
                self.log_message(f"🏛️ Вы нашли {gold_amount} золота в руинах!")
                self.update_quest_progress("gold", amount=gold_amount)
            if not obj.permanent:
                obj.collected = True
        
        elif obj.type == OBJECT_SHRINE:
            buff_type = random.choice(["attack", "defense", "hp"])
            if buff_type == "attack":
                self.hero.attack += 2
                self.log_message("🗿 Святилище усилило вашу атаку на 2!")
            elif buff_type == "defense":
                self.hero.defense += 2
                self.log_message("🗿 Святилище усилило вашу защиту на 2!")
            else:
                self.hero.max_hp += 20
                self.hero.hp += 20
                self.log_message(" Святилище увеличило ваше здоровье на 20!")
            if not obj.permanent:
                obj.collected = True
        
        elif obj.type == OBJECT_DRAGON_LAIR:
            self.log_message("🐉 Вы вошли в логово дракона! Будьте осторожны!")
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = self.hero.x + dx, self.hero.y + dy
                if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                    if self.game_map[ny][nx] in (TERRAIN_GRASS, TERRAIN_FOREST, TERRAIN_PATH):  # ← ДОБАВЬ
                        from enemy import Enemy
                        dragon = Enemy(nx, ny, "dragon", spawn_week=(self.turns // TURNS_PER_WEEK) + 1)
                        self.enemies.append(dragon)
                        self.log_message(f"🐉 Дракон появился!")
                        break
            if not obj.permanent:
                obj.collected = True
        
        elif obj.type == OBJECT_WATCHTOWER:
            for dy in range(-4, 5):
                for dx in range(-4, 5):
                    nx, ny = self.hero.x + dx, self.hero.y + dy
                    if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                        self.fog[ny][nx] = 2
            self.log_message("🗼 Сторожевая башня открыла большую область карты!")
            if not obj.permanent:
                obj.collected = True
        
        elif obj.type == OBJECT_MERCHANT:
            self.log_message("🏪 Торговец предлагает свои услуги! Нажмите M чтобы открыть магазин.")
            # НЕ помечаем как collected - permanent=True
        
        elif obj.type == OBJECT_MAGIC_WELL:
            self.hero.attack += 3
            self.hero.defense += 3
            self.log_message("⛲ Магический колодец усилил вас! +3 к атаке и защите")
            if not obj.permanent:
                obj.collected = True
    

    def _get_item_sell_price(self, item):
        """Рассчитывает цену продажи предмета (30% от базовой стоимости)"""
        base_value = 0
        
        if item.attack > 0:
            base_value += item.attack * 20
        if item.defense > 0:
            base_value += item.defense * 20
        if item.hp > 0:
            base_value += item.hp * 5
        
        # Множитель редкости
        rarity_multipliers = {
            "common": 1.0,
            "rare": 2.0,
            "epic": 3.5,
            "legendary": 5.0
        }
        base_value *= rarity_multipliers.get(item.rarity, 1.0)
        
        return max(10, int(base_value * 0.3))  # 30% от стоимости, минимум 10
    


    def _load_terrain_textures(self):
        """Загружает текстуры местности в кэш"""
        texture_files = {
            'grass': ['grass1.png', 'grass2.png', 'grass3.png'],
            'forest': ['forest1.png', 'forest2.png'],
            'water': ['water1.png', 'water2.png'],
            'mountain': ['mountain1.png'],
            'path': ['path1.png', 'path2.png']
        }
        
        for terrain_type, files in texture_files.items():
            self.terrain_textures[terrain_type] = []
            for filename in files:
                path = f"images/terrain/{filename}"
                try:
                    texture = arcade.load_texture(path)
                    self.terrain_textures[terrain_type].append(texture)
                except:
                    pass  # Если текстуры нет — используем fallback
        
        print(f"🎨 Загружено текстур: {sum(len(v) for v in self.terrain_textures.values())}")

    def on_update(self, delta_time):
        """Обновление анимаций каждый кадр"""
        self.combat_animator.update()