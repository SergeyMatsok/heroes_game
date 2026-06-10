import arcade
import os

# Кэш текстур предметов
ITEM_TEXTURE_CACHE = {}

def load_item_icon(item_type, rarity="common"):
    """Загружает иконку предмета"""
    cache_key = f"{item_type}_{rarity}"
    
    if cache_key in ITEM_TEXTURE_CACHE:
        return ITEM_TEXTURE_CACHE[cache_key]
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Пытаемся загрузить конкретную иконку
    image_path = os.path.join(script_dir, "images", "items", f"{item_type}_{rarity}.png")
    
    try:
        texture = arcade.load_texture(image_path)
        ITEM_TEXTURE_CACHE[cache_key] = texture
        return texture
    except FileNotFoundError:
        pass
    
    # Пытаемся загрузить общую иконку типа
    image_path = os.path.join(script_dir, "images", "items", f"{item_type}.png")
    
    try:
        texture = arcade.load_texture(image_path)
        ITEM_TEXTURE_CACHE[cache_key] = texture
        return texture
    except FileNotFoundError:
        pass
    
    # Если ничего не найдено - возвращаем None (будем рисовать эмодзи)
    ITEM_TEXTURE_CACHE[cache_key] = None
    return None