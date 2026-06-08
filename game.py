import arcade
import random

from settings import (
    TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE,
    TERRAIN_GRASS, TERRAIN_MOUNTAIN, TERRAIN_WATER, TERRAIN_FOREST,
    COLOR_GRASS, COLOR_GRASS_DETAIL, COLOR_MOUNTAIN, COLOR_MOUNTAIN_PEAK,
    COLOR_WATER, COLOR_WATER_WAVE, COLOR_FOREST, COLOR_GRID, COLOR_GOLD, COLOR_UI_BG,
    GOLD_PER_PILE, 
    UPGRADE_ATTACK_COST, UPGRADE_DEFENSE_COST, UPGRADE_HP_COST, UPGRADE_AMOUNT,
    XP_PER_KILL, ENEMY_AGGRO_RANGE, TURNS_PER_DAY, TURNS_PER_WEEK, WEEKS_TO_WIN, 
    ENEMIES_SPAWN_PER_WEEK, GOLD_SPAWN_PER_WEEK, POTION_SPAWN_PER_WEEK,
    ENEMY_WOLF_CHANCE, ENEMY_GOBLIN_CHANCE, ENEMY_SKELETON_CHANCE, 
    ENEMY_LICH_CHANCE, ENEMY_GOLEM_CHANCE, ENEMY_DRAGON_CHANCE
)
from map_generator import generate_map, generate_gold_positions, generate_potion_positions
from hero import Hero
from enemy import Enemy
from potion import Potion

# Размеры областей
CONSOLE_WIDTH = 350
UI_HEIGHT = 80
GAME_WIDTH = SCREEN_WIDTH   # Область игры
GAME_HEIGHT = SCREEN_HEIGHT

class HeroesGame(arcade.Window):
    def __init__(self):
        # Окно: консоль слева + игра справа, UI снизу
        total_width = CONSOLE_WIDTH + GAME_WIDTH
        total_height = GAME_HEIGHT + UI_HEIGHT
        super().__init__(total_width, total_height, SCREEN_TITLE)
        
        # Камера = просто смещение (без arcade.Camera!)
        self.camera_x = 0
        self.camera_y = 0
        
        self.messages = []
        self.max_messages = 8
        
        self.reset_game()
        arcade.set_background_color((10, 10, 15))
    
    def log_message(self, text):
        self.messages.append(text)
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
        print(text)
    
    def reset_game(self):
        self.game_map = generate_map()
        self.hero = Hero(0, 0)
        self.game_map[self.hero.y][self.hero.x] = TERRAIN_GRASS
        
        self.gold_positions = generate_gold_positions(self.game_map, self.hero.x, self.hero.y)
        self.potion_positions = generate_potion_positions(self.game_map, self.hero.x, self.hero.y, self.gold_positions)
        self.potions = [Potion(x, y) for x, y in self.potion_positions]
        self.enemies = self.generate_enemies()
        
        self.game_over = False
        self.victory = False
        self.shop_mode = False
        self.level_up_timer = 0
        self.turns = 0
        self.messages = []
        
        self.fog = [[0 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
        self.update_fog()
        self.update_camera()
        self.log_message("🏰 Добро пожаловать в Бесконечное Королевство!")
    
    def update_camera(self):
        """Смещаем камеру так, чтобы герой был в центре игровой области"""
        # Позиция героя в мировых координатах
        hero_world_x = self.hero.x * TILE_SIZE + TILE_SIZE // 2
        hero_world_y = self.hero.y * TILE_SIZE + TILE_SIZE // 2
        
        # Центр игровой области
        center_x = GAME_WIDTH / 2
        center_y = GAME_HEIGHT / 2
        
        # Смещение камеры
        self.camera_x = hero_world_x - center_x
        self.camera_y = hero_world_y - center_y
        
        # Ограничения (не выходить за границы карты)
        min_x = 0
        max_x = MAP_WIDTH * TILE_SIZE - GAME_WIDTH
        min_y = 0
        max_y = MAP_HEIGHT * TILE_SIZE - GAME_HEIGHT
        
        self.camera_x = max(min_x, min(self.camera_x, max_x))
        self.camera_y = max(min_y, min(self.camera_y, max_y))
    
    def advance_turn(self):
        self.turns += 1
        if self.turns > 0 and self.turns % TURNS_PER_WEEK == 0:
            self.spawn_weekly_resources_and_enemies()
        if self.turns >= WEEKS_TO_WIN * TURNS_PER_WEEK:
            self.game_over = True
            self.victory = True
    
    def spawn_weekly_resources_and_enemies(self):
        current_week = (self.turns // TURNS_PER_WEEK) + 1
        self.log_message(f" Неделя {current_week}: Появились новые ресурсы и враги!")
        
        for enemy in self.enemies:
            enemy.spawn_week = current_week
            enemy.update_stats()
        
        def spawn_item(item_type, count):
            for _ in range(count):
                for attempt in range(200):
                    x = random.randint(0, MAP_WIDTH - 1)
                    y = random.randint(0, MAP_HEIGHT - 1)
                    if (self.game_map[y][x] in (TERRAIN_GRASS, TERRAIN_FOREST) and
                        (x, y) != (self.hero.x, self.hero.y) and
                        (x, y) not in self.gold_positions and
                        (x, y) not in self.potion_positions and
                        not any(e.x == x and e.y == y for e in self.enemies)):
                        if item_type == "gold":
                            self.gold_positions.append((x, y))
                        elif item_type == "potion":
                            self.potions.append(Potion(x, y))
                        break
        
        spawn_item("gold", GOLD_SPAWN_PER_WEEK)
        spawn_item("potion", POTION_SPAWN_PER_WEEK)
        
        for _ in range(ENEMIES_SPAWN_PER_WEEK):
            for attempt in range(200):
                x = random.randint(0, MAP_WIDTH - 1)
                y = random.randint(0, MAP_HEIGHT - 1)
                if (self.game_map[y][x] in (TERRAIN_GRASS, TERRAIN_FOREST) and
                    (x, y) != (self.hero.x, self.hero.y) and
                    (x, y) not in self.gold_positions and
                    (x, y) not in self.potion_positions and
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
                    else:
                        self.enemies.append(Enemy(x, y, "dragon", current_week))
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
                while True:
                    x = random.randint(0, MAP_WIDTH - 1)
                    y = random.randint(0, MAP_HEIGHT - 1)
                    if (self.game_map[y][x] in (TERRAIN_GRASS, TERRAIN_FOREST) and 
                        (x, y) != (self.hero.x, self.hero.y) and
                        (x, y) not in self.gold_positions and (x, y) not in self.potion_positions and
                        not any(e.x == x and e.y == y for e in enemies)):
                        enemies.append(Enemy(x, y, enemy_type, spawn_week=1))
                        break
        add_enemy("wolf", 3)
        add_enemy("goblin", 5)
        add_enemy("skeleton", 3)
        add_enemy("lich", 2)
        add_enemy("golem", 2)
        add_enemy("dragon", 1)
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
                        if self.game_map[new_y][new_x] in (TERRAIN_GRASS, TERRAIN_FOREST):
                            is_blocked = any(e.x == new_x and e.y == new_y for e in self.enemies if e != enemy)
                            if not is_blocked:
                                enemy.x = new_x
                                enemy.y = new_y
    
    def draw_terrain_tile(self, x, y, terrain_type, screen_x, screen_y):
        if terrain_type == TERRAIN_GRASS:
            arcade.draw_lbwh_rectangle_filled(screen_x, screen_y, TILE_SIZE, TILE_SIZE, COLOR_GRASS)
            if (x + y * 3) % 4 == 0:
                arcade.draw_circle_filled(screen_x + 16, screen_y + 16, 3, COLOR_GRASS_DETAIL)
            if (x * 2 + y) % 5 == 0:
                arcade.draw_circle_filled(screen_x + 48, screen_y + 40, 4, COLOR_GRASS_DETAIL)
        elif terrain_type == TERRAIN_MOUNTAIN:
            arcade.draw_lbwh_rectangle_filled(screen_x, screen_y, TILE_SIZE, TILE_SIZE, COLOR_MOUNTAIN)
            points = [(screen_x + TILE_SIZE//2, screen_y + TILE_SIZE - 10),
                      (screen_x + 10, screen_y + 20),
                      (screen_x + TILE_SIZE - 10, screen_y + 20)]
            arcade.draw_polygon_filled(points, COLOR_MOUNTAIN_PEAK)
        elif terrain_type == TERRAIN_WATER:
            arcade.draw_lbwh_rectangle_filled(screen_x, screen_y, TILE_SIZE, TILE_SIZE, COLOR_WATER)
            arcade.draw_arc_outline(screen_x + 16, screen_y + 20, 20, 10, COLOR_WATER_WAVE, 0, 180, 2)
            arcade.draw_arc_outline(screen_x + 48, screen_y + 40, 20, 10, COLOR_WATER_WAVE, 0, 180, 2)
        elif terrain_type == TERRAIN_FOREST:
            arcade.draw_lbwh_rectangle_filled(screen_x, screen_y, TILE_SIZE, TILE_SIZE, COLOR_FOREST)
    
    def on_draw(self):
        self.clear()
        
        # ==========================================
        # ЗОНА 1: КОНСОЛЬ (слева, фиксированная)
        # Координаты: x от 0 до CONSOLE_WIDTH, y от UI_HEIGHT до height
        # ==========================================
        console_bg_x = CONSOLE_WIDTH / 2
        console_bg_y = UI_HEIGHT + (GAME_HEIGHT / 2)
        arcade.draw_lbwh_rectangle_filled(console_bg_x, console_bg_y, CONSOLE_WIDTH, GAME_HEIGHT, (15, 15, 20))
        arcade.draw_lbwh_rectangle_outline(console_bg_x, console_bg_y, CONSOLE_WIDTH, GAME_HEIGHT, (80, 80, 80), 2)
        
        arcade.draw_text("📜 ЖУРНАЛ СОБЫТИЙ", 15, self.height - 40, arcade.color.GOLD, 14, font_name="Arial", bold=True)
        arcade.draw_line(10, self.height - 55, CONSOLE_WIDTH - 15, self.height - 55, (100, 100, 100), 1)
        
        y_offset = self.height - 80
        for i, msg in enumerate(reversed(self.messages)):
            display_msg = msg[:45] + ("..." if len(msg) > 45 else "")
            arcade.draw_text(display_msg, 15, y_offset - (i * 20), arcade.color.LIGHT_GRAY, 12, font_name="Arial")
        
        # ==========================================
        # ЗОНА 2: НИЖНЯЯ ПАНЕЛЬ (снизу, фиксированная)
        # Координаты: x от CONSOLE_WIDTH до width, y от 0 до UI_HEIGHT
        # ==========================================
        ui_center_x = CONSOLE_WIDTH + GAME_WIDTH / 2
        ui_center_y = UI_HEIGHT / 2
        arcade.draw_lbwh_rectangle_filled(ui_center_x, ui_center_y, GAME_WIDTH, UI_HEIGHT, COLOR_UI_BG)
        arcade.draw_line(CONSOLE_WIDTH, UI_HEIGHT, self.width, UI_HEIGHT, (80, 80, 80), 2)
        
        current_day = (self.turns // TURNS_PER_DAY) + 1
        current_week = (self.turns // TURNS_PER_WEEK) + 1
        
        if not self.shop_mode:
            arcade.draw_text(f"📅 Неделя: {current_week}, День: {current_day} | Ход: {self.turns}", 
                             CONSOLE_WIDTH + 15, 50, arcade.color.WHITE, 13, font_name="Arial", bold=True)
            arcade.draw_text(f"Ур: {self.hero.level} | 💰: {self.hero.gold} | ❤️: {self.hero.hp}/{self.hero.max_hp}", 
                             ui_center_x, 30, arcade.color.WHITE, 13, font_name="Arial", anchor_x="center")
            arcade.draw_text(f"⚔️: {self.hero.attack} | ️: {self.hero.defense} | : {len(self.enemies)} | [M] Магазин", 
                             self.width - 380, 30, arcade.color.LIGHT_GRAY, 12, font_name="Arial")
        else:
            arcade.draw_text(f"🏰 МАГАЗИН | 💰: {self.hero.gold}", ui_center_x, 50, arcade.color.GOLD, 14, font_name="Arial", bold=True, anchor_x="center")
            arcade.draw_text(f"[1] Атака +{UPGRADE_AMOUNT} ({UPGRADE_ATTACK_COST}g) | [2] Защита +{UPGRADE_AMOUNT} ({UPGRADE_DEFENSE_COST}g) | [3] HP +{UPGRADE_AMOUNT*2} ({UPGRADE_HP_COST}g) | [ESC] Закрыть", 
                             ui_center_x, 30, arcade.color.LIGHT_GRAY, 12, font_name="Arial", anchor_x="center")
        
        # ==========================================
        # ЗОНА 3: ИГРА (справа сверху, со смещением камеры)
        # Координаты: x от CONSOLE_WIDTH до width, y от UI_HEIGHT до height
        # Всё рисуется со смещением (self.camera_x, self.camera_y)
        # ==========================================
        
        # Обрезаем область рисования игры (чтобы не вылезало за границы)
        # Рисуем рамку игровой области
        game_area_x = CONSOLE_WIDTH + GAME_WIDTH / 2
        game_area_y = UI_HEIGHT + GAME_HEIGHT / 2
        arcade.draw_lbwh_rectangle_outline(game_area_x, game_area_y, GAME_WIDTH, GAME_HEIGHT, (60, 60, 60), 2)
        
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                # Мировые координаты клетки
                world_x = x * TILE_SIZE
                world_y = y * TILE_SIZE
                
                # Экраные координаты (со смещением камеры + смещение зоны игры)
                screen_x = CONSOLE_WIDTH + world_x - self.camera_x
                screen_y = UI_HEIGHT + world_y - self.camera_y
                
                # Пропускаем если вне видимой области
                if screen_x < CONSOLE_WIDTH - TILE_SIZE or screen_x > self.width + TILE_SIZE:
                    continue
                if screen_y < UI_HEIGHT - TILE_SIZE or screen_y > self.height + TILE_SIZE:
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
        
        for gold_x, gold_y in self.gold_positions:
            if self.fog[gold_y][gold_x] == 2:
                screen_x = CONSOLE_WIDTH + gold_x * TILE_SIZE - self.camera_x
                screen_y = UI_HEIGHT + gold_y * TILE_SIZE - self.camera_y
                arcade.draw_text("💰", screen_x + TILE_SIZE//2 + 2, screen_y + TILE_SIZE//2 - 2, (0,0,0,100), 28, anchor_x="center", anchor_y="center")
                arcade.draw_text("💰", screen_x + TILE_SIZE//2, screen_y + TILE_SIZE//2, arcade.color.WHITE, 28, anchor_x="center", anchor_y="center")
        
        for potion in self.potions:
            if self.fog[potion.y][potion.x] == 2:
                screen_x = CONSOLE_WIDTH + potion.x * TILE_SIZE - self.camera_x
                screen_y = UI_HEIGHT + potion.y * TILE_SIZE - self.camera_y
                arcade.draw_text("", screen_x + TILE_SIZE//2 + 2, screen_y + TILE_SIZE//2 - 2, (0,0,0,100), 32, anchor_x="center", anchor_y="center")
                arcade.draw_text("🧪", screen_x + TILE_SIZE//2, screen_y + TILE_SIZE//2, arcade.color.WHITE, 32, anchor_x="center", anchor_y="center")
        
        for enemy in self.enemies:
            if self.fog[enemy.y][enemy.x] == 2:
                screen_x = CONSOLE_WIDTH + enemy.x * TILE_SIZE - self.camera_x
                screen_y = UI_HEIGHT + enemy.y * TILE_SIZE - self.camera_y
                enemy.draw(screen_x, screen_y)
        
        hero_screen_x = CONSOLE_WIDTH + self.hero.x * TILE_SIZE - self.camera_x
        hero_screen_y = UI_HEIGHT + self.hero.y * TILE_SIZE - self.camera_y
        self.hero.draw(hero_screen_x, hero_screen_y)
        
        # Сообщения о конце игры (поверх всего)
        if self.game_over:
            if self.victory:
                msg = f"🏆 ПОБЕДА! Вы успешно правили {WEEKS_TO_WIN} недель!"
                color = arcade.color.GREEN
            else:
                msg = f"💀 ПОРАЖЕНИЕ! Герой пал в бою..."
                color = arcade.color.RED
            arcade.draw_text(msg, ui_center_x, self.height / 2, color, 28, anchor_x="center", font_name="Arial", bold=True)
            arcade.draw_text("Нажмите R для новой игры", ui_center_x, self.height / 2 - 40, arcade.color.WHITE, 18, anchor_x="center", font_name="Arial")
    
    def on_key_press(self, key, modifiers):
        if self.game_over and key == arcade.key.R:
            self.reset_game()
            return
        if self.game_over: return
        
        if self.shop_mode:
            if key == arcade.key.ESCAPE: 
                self.shop_mode = False
            elif key == arcade.key.KEY_1 and self.hero.upgrade_attack(): 
                self.log_message(f"️ Атака улучшена! Теперь: {self.hero.attack}")
            elif key == arcade.key.KEY_2 and self.hero.upgrade_defense(): 
                self.log_message(f"🛡️ Защита улучшена! Теперь: {self.hero.defense}")
            elif key == arcade.key.KEY_3 and self.hero.upgrade_hp(): 
                self.log_message(f"❤️ Здоровье улучшено! Теперь: {self.hero.max_hp}")
            return
        
        if key == arcade.key.M:
            self.shop_mode = True
            return
        
        new_x, new_y = self.hero.x, self.hero.y
        if key in (arcade.key.W, arcade.key.UP) and self.hero.y < MAP_HEIGHT - 1: new_y += 1
        elif key in (arcade.key.S, arcade.key.DOWN) and self.hero.y > 0: new_y -= 1
        elif key in (arcade.key.A, arcade.key.LEFT) and self.hero.x > 0: new_x -= 1
        elif key in (arcade.key.D, arcade.key.RIGHT) and self.hero.x < MAP_WIDTH - 1: new_x += 1
        
        action_taken = False
        
        if self.game_map[new_y][new_x] in (TERRAIN_GRASS, TERRAIN_FOREST):
            enemy_on_cell = next((e for e in self.enemies if e.x == new_x and e.y == new_y), None)
            if enemy_on_cell:
                self.combat(enemy_on_cell)
                action_taken = True
            else:
                self.hero.x = new_x
                self.hero.y = new_y
                action_taken = True
                if (self.hero.x, self.hero.y) in self.gold_positions:
                    self.gold_positions.remove((self.hero.x, self.hero.y))
                    self.hero.gold += GOLD_PER_PILE
                    self.log_message("💰 Вы нашли золото!")
                potion_on_cell = next((p for p in self.potions if p.x == self.hero.x and p.y == self.hero.y), None)
                if potion_on_cell:
                    self.hero.heal(potion_on_cell.heal_amount)
                    self.potions.remove(potion_on_cell)
                    self.log_message(f"🧪 Вы выпили зелье! HP: {self.hero.hp}/{self.hero.max_hp}")
        
        if action_taken:
            self.advance_turn()
            self.update_fog()
            self.update_enemies()
            self.update_camera()
    
    def combat(self, enemy):
        damage_to_enemy = enemy.take_damage(self.hero.attack)
        if enemy.is_alive():
            self.hero.take_damage(enemy.attack)
            if not self.hero.is_alive():
                self.game_over = True
                self.victory = False
        else:
            self.enemies.remove(enemy)
            self.log_message(f"🏆 Вы победили {enemy.emoji} и получили {XP_PER_KILL} XP!")
            if self.hero.gain_xp(XP_PER_KILL):
                self.level_up_timer = 120
                self.log_message(f"🎉 Уровень повышен! Теперь вы {self.hero.level} уровня!")
            self.update_fog()
            self.update_enemies()
            self.update_camera()