import arcade
from items import (RARITY_COLORS, RARITY_NAMES, 
                   ITEM_TYPE_WEAPON, ITEM_TYPE_ARMOR, ITEM_TYPE_ACCESSORY)

# Размеры
SLOT_SIZE = 60
SLOT_PADDING = 10
ICON_SIZE = 40
hovered_inventory_item = None
hovered_inventory_slot = None

# Иконки для типов предметов (эмодзи как fallback)
ITEM_ICONS = {
    ITEM_TYPE_WEAPON: "⚔️",
    ITEM_TYPE_ARMOR: "🛡️",
    ITEM_TYPE_ACCESSORY: "💍"
}

SLOT_NAMES = {
    ITEM_TYPE_WEAPON: "Оружие",
    ITEM_TYPE_ARMOR: "Броня",
    ITEM_TYPE_ACCESSORY: "Аксессуар"
}



def draw_item_tooltip(x, y, item):
    """Рисует подсказку для предмета"""
    if not item:
        return
    
    lines = [f"🎁 {item.name}"]
    
    if item.attack > 0:
        lines.append(f"⚔️ Атака: +{item.attack}")
    if item.defense > 0:
        lines.append(f"🛡️ Защита: +{item.defense}")
    if item.hp > 0:
        lines.append(f"❤️ Здоровье: +{item.hp}")
    
    rarity_names = {"common": "Обычный", "rare": "Редкий", "epic": "Эпический", "legendary": "Легендарный"}
    lines.append(f"📊 {rarity_names.get(item.rarity, item.rarity)}")
    
    # Рассчитываем цену продажи
    base_value = 0
    if item.attack > 0:
        base_value += item.attack * 20
    if item.defense > 0:
        base_value += item.defense * 20
    if item.hp > 0:
        base_value += item.hp * 5
    
    rarity_multipliers = {"common": 1.0, "rare": 2.0, "epic": 3.5, "legendary": 5.0}
    base_value *= rarity_multipliers.get(item.rarity, 1.0)
    sell_price = max(10, int(base_value * 0.3))
    
    lines.append(f"💰 Цена продажи: {sell_price} золота")
    
    # Рисуем подсказку
    max_width = max(len(line) * 9 for line in lines) + 20
    total_height = len(lines) * 20 + 10
    
    # Ограничиваем экраном
    tooltip_x = x + 15
    tooltip_y = y + 10
    
    # Рисуем фон
    arcade.draw_lbwh_rectangle_filled(
        tooltip_x, tooltip_y, max_width, total_height,
        (20, 20, 30, 240)
    )
    arcade.draw_lbwh_rectangle_outline(
        tooltip_x, tooltip_y, max_width, total_height,
        (150, 150, 150), 1
    )
    
    # Рисуем текст
    text_y = tooltip_y + total_height - 10
    for i, line in enumerate(lines):
        color = (255, 215, 0) if i == 0 else arcade.color.LIGHT_GRAY
        arcade.draw_text(
            line,
            tooltip_x + max_width // 2, text_y,
            color, 11,
            anchor_x="center", anchor_y="top",
            font_name="Arial"
        )
        text_y -= 20

def draw_rect_centered(x, y, width, height, color, outline_color=None, outline_width=2):
    """Рисует прямоугольник с ЦЕНТРОМ в точке (x, y)"""
    # Для draw_lbwh_rectangle нужны left, bottom, width, height
    left = x - width / 2
    bottom = y - height / 2
    arcade.draw_lbwh_rectangle_filled(left, bottom, width, height, color)
    if outline_color:
        arcade.draw_lbwh_rectangle_outline(left, bottom, width, height, outline_color, outline_width)


def draw_inventory(game):
    """Рисует интерфейс инвентаря"""
    W = game.width
    H = game.height
    
    panel_width = 900
    panel_height = 600
    
    # Центр экрана
    cx = W / 2
    cy = H / 2
    
    # Координаты панели
    panel_left = cx - panel_width / 2      # ← ЭТО УЖЕ ЕСТЬ!
    panel_right = cx + panel_width / 2
    panel_top = cy + panel_height / 2
    panel_bottom = cy - panel_height / 2
    
    # Фон
    points = [(panel_left, panel_bottom), (panel_right, panel_bottom), 
              (panel_right, panel_top), (panel_left, panel_top)]
    arcade.draw_polygon_filled(points, (5, 5, 15, 255))
    arcade.draw_polygon_outline(points, (100, 100, 255), 2)
    
    # Заголовок
    arcade.draw_text(
        "🎒 ИНВЕНТАРЬ",
        cx, panel_top - 40,
        arcade.color.GOLD, 24,
        anchor_x="center", anchor_y="top",
        font_name="Arial", bold=True
    )
    
    # === РИСУЕМ ПОРТРЕТ ПЕРСОНАЖА ПО ЦЕНТРУ ===
    try:
        # Загружаем текстуру персонажа
        hero_texture = arcade.load_texture("images/hero_portrait.png")
        
        # Центрируем портрет в панели
        portrait_x = cx  # Центр по X
        portrait_y = cy + 30  # Чуть выше центра по Y
        
        # Рисуем изображение через draw_texture_rect
        scale = 0.4
        width = int(hero_texture.width * scale)
        height = int(hero_texture.height * scale)
        
        # Вычисляем левый нижний угол для центрирования
        left = portrait_x - width // 2
        bottom = portrait_y - height // 2
        
        rect = arcade.XYWH(left, bottom, width, height)
        arcade.draw_texture_rect(hero_texture, rect)
        
        # Инфо о персонаже ПОД изображением
        arcade.draw_text(
            f"Уровень: {game.hero.level}",
            portrait_x, portrait_y - 90,
            arcade.color.GOLD, 14,
            anchor_x="center", font_name="Arial", bold=True
        )
        arcade.draw_text(
            f"❤️ {game.hero.hp}/{game.hero.max_hp}",
            portrait_x, portrait_y - 110,
            arcade.color.RED, 12,
            anchor_x="center", font_name="Arial"
        )
        arcade.draw_text(
            f"⚔️ {game.hero.attack} | 🛡️ {game.hero.defense}",
            portrait_x, portrait_y - 130,
            arcade.color.WHITE, 12,
            anchor_x="center", font_name="Arial"
        )
        arcade.draw_text(
            f"💰 {game.hero.gold} золота",
            portrait_x, portrait_y - 150,
            (255, 215, 0), 12,
            anchor_x="center", font_name="Arial"
        )
    except Exception as e:
        # Если текстуры нет, рисуем заглушку
        print(f"⚠️ Не удалось загрузить портрет: {e}")
        arcade.draw_text(
            "👤",
            cx, cy + 30,
            arcade.color.WHITE, 100,
            anchor_x="center", anchor_y="center"
        )
        # Инфо о персонаже
        arcade.draw_text(
            f"Уровень: {game.hero.level}",
            cx, cy - 60,
            arcade.color.GOLD, 14,
            anchor_x="center", font_name="Arial", bold=True
        )
        arcade.draw_text(
            f"❤️ {game.hero.hp}/{game.hero.max_hp} | ⚔️ {game.hero.attack} | 🛡️ {game.hero.defense}",
            cx, cy - 80,
            arcade.color.WHITE, 12,
            anchor_x="center", font_name="Arial"
        )
        arcade.draw_text(
            f"💰 {game.hero.gold} золота",
            cx, cy - 100,
            (255, 215, 0), 12,
            anchor_x="center", font_name="Arial"
        )
    
    # === ЛЕВАЯ ЧАСТЬ - ЭКИПИРОВКА ===
    left_x = panel_left + 100
    
    arcade.draw_text(
        "📌 ЭКИПИРОВКА",
        left_x, panel_top - 100,
        arcade.color.CYAN, 16,
        anchor_x="left", font_name="Arial", bold=True
    )
    
    slot_y = panel_top - 180
    draw_equipment_slot(left_x, slot_y, game.hero.equipped_weapon, ITEM_TYPE_WEAPON, "Оружие")
    slot_y -= 130
    draw_equipment_slot(left_x, slot_y, game.hero.equipped_armor, ITEM_TYPE_ARMOR, "Броня")
    slot_y -= 130
    draw_equipment_slot(left_x, slot_y, game.hero.equipped_accessory, ITEM_TYPE_ACCESSORY, "Аксессуар")
    
    draw_bonuses(left_x, panel_bottom + 80, game.hero)
    
    # === ПРАВАЯ ЧАСТЬ - ИНВЕНТАРЬ ===
    right_x = cx + 100
    
    inv_count = len(game.hero.inventory)
    arcade.draw_text(
        f"📦 ПРЕДМЕТЫ ({inv_count}/{game.hero.max_inventory})",
        right_x, panel_top - 100,
        arcade.color.CYAN, 16,
        anchor_x="left", font_name="Arial", bold=True
    )
    
    slots_per_row = 5
    start_x = right_x
    start_y = panel_top - 180
    
    for i, item in enumerate(game.hero.inventory):
        row = i // slots_per_row
        col = i % slots_per_row
        
        x = start_x + col * (SLOT_SIZE + SLOT_PADDING)
        y = start_y - row * (SLOT_SIZE + SLOT_PADDING)
        
        draw_inventory_slot(x, y, item, i)
    
    # Подсказки
    if game.is_near_merchant():
        hint_text = "ЛКМ - экипировать | ПКМ - продать | ESC - закрыть"
    else:
        hint_text = "ЛКМ - экипировать | Найдите магазин для продажи | ESC - закрыть"
    
    arcade.draw_text(
        hint_text,
        cx, panel_bottom + 40,
        (150, 150, 150), 12,
        anchor_x="center", font_name="Arial"
    )


def draw_equipment_slot(x, y, item, item_type, slot_name):
    """Рисует слот экипировки"""
    icon = ITEM_ICONS.get(item_type, "")
    
    # === ОТЛАДКА: рисуем точки ===
    # Красная точка - центр слота (x, y)
    arcade.draw_circle_filled(x, y, 4, (255, 0, 0))
    # ============================
    
    if item:
        color = item.get_color()
        # Подсветка
        draw_rect_centered(
            x, y, SLOT_SIZE + 4, SLOT_SIZE + 4,
            (color[0], color[1], color[2], 50),
            color, 3
        )
        
        # Рисуем иконку предмета
        texture = item.get_icon()
        if texture:
            # Масштабируем
            scale = min(ICON_SIZE / texture.width, ICON_SIZE / texture.height)
            scaled_width = int(texture.width * scale)
            scaled_height = int(texture.height * scale)
            
            # Используем LBWH (Left, Bottom, Width, Height) - те же координаты что и для квадрата!
            left = x - scaled_width / 2
            bottom = y - scaled_height / 2
            rect = arcade.LBWH(left, bottom, scaled_width, scaled_height)
            arcade.draw_texture_rect(texture, rect)
        else:
            arcade.draw_text(
                icon, x, y,
                (255, 255, 255), 28,
                anchor_x="center", anchor_y="center"
            )
        # Название и статы справа от слота
        info_x = x + SLOT_SIZE // 2 + 20
        
        arcade.draw_text(
            item.name[:20],
            info_x, y + 10,
            color, 12,
            anchor_x="left", font_name="Arial", bold=True
        )
        
        stats = []
        if item.attack > 0:
            stats.append(f"⚔️+{item.attack}")
        if item.defense > 0:
            stats.append(f"🛡️+{item.defense}")
        if item.hp > 0:
            stats.append(f"❤️+{item.hp}")
        
        if stats:
            arcade.draw_text(
                "  ".join(stats),
                info_x, y - 10,
                (220, 220, 220), 11,
                anchor_x="left", font_name="Arial"
            )
        
        rarity_name = RARITY_NAMES.get(item.rarity, "")
        arcade.draw_text(
            rarity_name,
            info_x, y - 25,
            color, 10,
            anchor_x="left", font_name="Arial", italic=True
        )
    else:
        # Пустой слот (центрированный!)
        draw_rect_centered(
            x, y, SLOT_SIZE, SLOT_SIZE,
            (25, 25, 40),
            (70, 70, 90), 2
        )
        
        arcade.draw_text(
            icon, x, y,
            (90, 90, 110), 24,
            anchor_x="center", anchor_y="center"
        )
        
        # Подпись слота
        arcade.draw_text(
            slot_name,
            x, y - SLOT_SIZE//2 - 5,
            (100, 100, 100), 10,
            anchor_x="center", anchor_y="top",
            font_name="Arial"
        )


def draw_inventory_slot(x, y, item, index):
    """Рисует слот предмета в инвентаре. (x, y) - ЦЕНТР слота"""
    color = item.get_color()
    
    # Фон слота (центрированный!)
    draw_rect_centered(
        x, y, SLOT_SIZE, SLOT_SIZE,
        (30, 30, 50),
        color, 2
    )
    
    # Рисуем иконку предмета (центрированную)
    # Рисуем иконку предмета
    texture = item.get_icon()
    if texture:
        scale = min(ICON_SIZE / texture.width, ICON_SIZE / texture.height)
        scaled_width = int(texture.width * scale)
        scaled_height = int(texture.height * scale)
        
        # Используем LBWH (Left, Bottom, Width, Height)
        left = x - scaled_width / 2
        bottom = y - scaled_height / 2
        rect = arcade.LBWH(left, bottom, scaled_width, scaled_height)
        arcade.draw_texture_rect(texture, rect)
    else:
        icon = ITEM_ICONS.get(item.type, "📦")
        arcade.draw_text(
            icon, x, y,
            (255, 255, 255), 24,
            anchor_x="center", anchor_y="center"
        )
    
    # Номер слота
    arcade.draw_text(
        str(index + 1),
        x + SLOT_SIZE//2 - 8, y - SLOT_SIZE//2 + 8,
        (130, 130, 130), 9,
        anchor_x="right", anchor_y="top",
        font_name="Arial"
    )


def draw_bonuses(x, y, hero):
    """Рисует бонусы от экипировки"""
    arcade.draw_text(
        "📊 БОНУСЫ:",
        x, y,
        arcade.color.GREEN, 13,
        anchor_x="left", font_name="Arial", bold=True
    )
    
    bonuses_y = y - 25
    bonuses = []
    
    if hero.bonus_attack > 0:
        bonuses.append(f"⚔️ Атака: +{hero.bonus_attack}")
    if hero.bonus_defense > 0:
        bonuses.append(f"🛡️ Защита: +{hero.bonus_defense}")
    if hero.bonus_hp > 0:
        bonuses.append(f"❤️ Здоровье: +{hero.bonus_hp}")
    
    if bonuses:
        for i, bonus_text in enumerate(bonuses):
            arcade.draw_text(
                bonus_text,
                x + 10, bonuses_y - (i * 20),
                (180, 255, 180), 11,
                anchor_x="left", font_name="Arial"
            )
    else:
        arcade.draw_text(
            "Нет экипировки",
            x + 10, bonuses_y,
            (120, 120, 120), 11,
            anchor_x="left", font_name="Arial", italic=True
        )