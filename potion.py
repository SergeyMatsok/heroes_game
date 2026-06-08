import arcade
from settings import TILE_SIZE, COLOR_POTION, POTION_HEAL_AMOUNT

class Potion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.heal_amount = POTION_HEAL_AMOUNT
    
    def draw(self, screen_x, screen_y):
        """Отрисовка зелья"""
        # Рисуем зеленое зелье в виде круга
        center_x = screen_x + TILE_SIZE // 2
        center_y = screen_y + TILE_SIZE // 2
        
        # Внешний круг (бутылка)
        arcade.draw_circle_filled(center_x, center_y, 20, COLOR_POTION)
        arcade.draw_circle_outline(center_x, center_y, 20, (0, 100, 0), 2)
        
        # Крестик внутри (медицинский символ)
        arcade.draw_line(center_x - 8, center_y, center_x + 8, center_y, (255, 255, 255), 3)
        arcade.draw_line(center_x, center_y - 8, center_x, center_y + 8, (255, 255, 255), 3)