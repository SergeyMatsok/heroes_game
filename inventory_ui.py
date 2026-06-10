import arcade
from items import (RARITY_COLORS, RARITY_NAMES, 
                   ITEM_TYPE_WEAPON, ITEM_TYPE_ARMOR, ITEM_TYPE_ACCESSORY)

# Размеры
SLOT_SIZE = 60
SLOT_PADDING = 10
ICON_SIZE = 40

# Иконки для типов предметов (эмодзи как fallback)
ITEM_ICONS = {
    ITEM_TYPE_WEAPON: "️",
    ITEM_TYPE_ARMOR: "🛡️",
    ITEM_TYPE_ACCESSORY: "💍"
}

SLOT_NAMES = {
    ITEM_TYPE_WEAPON: "Оружие",
    ITEM_TYPE_ARMOR: "Броня",
    ITEM_TYPE_ACCESSORY: "Аксессуар"
}

def draw_inventory(game):
    """Рисует интерфейс инвентаря"""
    W = game.width
    H = game.height
    
    panel_width = 900
    panel_height = 600
    
    # Центр экрана
    cx = W / 2
    cy = H / 2
    
    # Фон - РИСУЕМ ПРЯМОУГОЛЬНИК ЧЕРЕЗ УГЛЫ
    left = cx - panel_width / 2
    right = cx + panel_width / 2
    top = cy + panel_height / 2
    bottom = cy - panel_height / 2
    
    # Фон (через draw_rectangle)
    points = [(left, bottom), (right, bottom), (right, top), (left, top)]
    arcade.draw_polygon_filled(points, (5, 5, 15, 255))
    
    # Рамка
    arcade.draw_polygon_outline(points, (100, 100, 255), 2)
    
    # Заголовок
    arcade.draw_text(
        "🎒 ИНВЕНТАРЬ",
        cx, top - 40,
        arcade.color.GOLD, 24,
        anchor_x="center", anchor_y="top",
        font_name="Arial", bold=True
    )
    
    # === ЛЕВАЯ ЧАСТЬ - ЭКИПИРОВКА ===
    left_x = left + 100
    
    arcade.draw_text(
        "📌 ЭКИПИРОВКА",
        left_x, top - 100,
        arcade.color.CYAN, 16,
        anchor_x="left", font_name="Arial", bold=True
    )
    
    slot_y = top - 180
    draw_equipment_slot(left_x, slot_y, game.hero.equipped_weapon, ITEM_TYPE_WEAPON, "Оружие")
    slot_y -= 130
    draw_equipment_slot(left_x, slot_y, game.hero.equipped_armor, ITEM_TYPE_ARMOR, "Броня")
    slot_y -= 130
    draw_equipment_slot(left_x, slot_y, game.hero.equipped_accessory, ITEM_TYPE_ACCESSORY, "Аксессуар")
    
    draw_bonuses(left_x, bottom + 80, game.hero)
    
    # === ПРАВАЯ ЧАСТЬ - ИНВЕНТАРЬ ===
    right_x = cx + 100
    
    inv_count = len(game.hero.inventory)
    arcade.draw_text(
        f"📦 ПРЕДМЕТЫ ({inv_count}/{game.hero.max_inventory})",
        right_x, top - 100,
        arcade.color.CYAN, 16,
        anchor_x="left", font_name="Arial", bold=True
    )
    
    slots_per_row = 5
    start_x = right_x
    start_y = top - 180
    
    for i, item in enumerate(game.hero.inventory):
        row = i // slots_per_row
        col = i % slots_per_row
        
        x = start_x + col * (SLOT_SIZE + SLOT_PADDING)
        y = start_y - row * (SLOT_SIZE + SLOT_PADDING)
        
        draw_inventory_slot(x, y, item, i)
    
    # Подсказки
    arcade.draw_text(
        "Кликни на предмет чтобы экипировать | ESC - закрыть",
        cx, bottom + 40,
        (150, 150, 150), 12,
        anchor_x="center", font_name="Arial"
    )
def draw_equipment_slot(x, y, item, item_type, slot_name):
    """Рисует слот экипировки"""
    icon = ITEM_ICONS.get(item_type, "")
    
    if item:
        color = item.get_color()
        # Подсветка
        arcade.draw_lbwh_rectangle_filled(
            x, y, SLOT_SIZE + 4, SLOT_SIZE + 4,
            (color[0], color[1], color[2], 50)
        )
        arcade.draw_lbwh_rectangle_outline(
            x, y, SLOT_SIZE + 4, SLOT_SIZE + 4,
            color, 3
        )
        
        # Рисуем иконку предмета
        texture = item.get_icon()
        if texture:
            scale = min(ICON_SIZE / texture.width, ICON_SIZE / texture.height)
            rect = arcade.XYWH(x, y, texture.width * scale, texture.height * scale)
            arcade.draw_texture_rect(texture, rect)
        else:
            arcade.draw_text(
                icon, x, y + 5,
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
        # Пустой слот
        arcade.draw_lbwh_rectangle_filled(
            x, y, SLOT_SIZE, SLOT_SIZE,
            (25, 25, 40)
        )
        arcade.draw_lbwh_rectangle_outline(
            x, y, SLOT_SIZE, SLOT_SIZE,
            (70, 70, 90), 2
        )
        
        arcade.draw_text(
            icon, x, y + 5,
            (90, 90, 110), 24,
            anchor_x="center", anchor_y="center"
        )
        # Подпись слота (ПОДНЯТА ВЫШЕ, ближе к квадрату)
        arcade.draw_text(
            slot_name,
            x, y - SLOT_SIZE//2 - 0,  # Было -15, стало -5
            (100, 100, 100), 10,
            anchor_x="center", anchor_y="top",
            font_name="Arial"
        )


def draw_inventory_slot(x, y, item, index):
    """Рисует слот предмета в инвентаре"""
    color = item.get_color()
    
    # Фон слота
    arcade.draw_lbwh_rectangle_filled(
        x, y, SLOT_SIZE, SLOT_SIZE,
        (30, 30, 50)
    )
    arcade.draw_lbwh_rectangle_outline(
        x, y, SLOT_SIZE, SLOT_SIZE,
        color, 2
    )
    
    # Рисуем иконку предмета
    texture = item.get_icon()
    if texture:
        scale = min(ICON_SIZE / texture.width, ICON_SIZE / texture.height)
        rect = arcade.XYWH(x, y, texture.width * scale, texture.height * scale)
        arcade.draw_texture_rect(texture, rect)
    else:
        icon = ITEM_ICONS.get(item.type, "📦")
        arcade.draw_text(
            icon, x, y + 5,
            (255, 255, 255), 24,
            anchor_x="center", anchor_y="center"
        )
    
    # НОВОЕ: Отображаем редкость предмета (внизу слота)
    rarity_name = RARITY_NAMES.get(item.rarity, "")
    if rarity_name:
        arcade.draw_text(
            rarity_name[:3].upper(),  # Первые 3 буквы: ОБЫ, РЕД, ЭПИ, ЛЕГ
            x, y - SLOT_SIZE//2 + 8,
            color, 8,
            anchor_x="center", anchor_y="top",
            font_name="Arial", bold=True
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
        bonuses.append(f"️ Атака: +{hero.bonus_attack}")
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