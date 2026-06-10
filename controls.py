import arcade

# Список всех управлений
CONTROLS = [
    ("🎮 Движение", [
        ("W / ↑", "Движение вверх"),
        ("S / ↓", "Движение вниз"),
        ("A / ←", "Движение влево"),
        ("D / →", "Движение вправо"),
    ]),
    
    ("⚔️ Бой и взаимодействие", [
        ("Идти в сторону врага", "Атаковать врага"),
        ("M", "Открыть/закрыть магазин"),
        ("1, 2, 3", "Улучшения в магазине"),
    ]),
    
    ("💾 Сохранение", [
        ("F5", "Сохранить игру"),
        ("F9", "Загрузить игру"),
        ("R", "Начать заново (после смерти)"),
    ]),
    
    ("🖥️ Интерфейс", [
        ("F11", "Полноэкранный режим"),
        ("F1 / H", "Показать/скрыть подсказки"),
        ("ESC", "Закрыть магазин/меню"),
    ]),
    
    ("📊 Информация", [
        ("Левая панель", "Журнал событий и квесты"),
        ("Нижняя панель", "Статистика героя"),
    ])
]

def draw_controls_panel():
    """Рисует панель с подсказками"""
    # Фон (полупрозрачный)
    # arcade.draw_lbwh_rectangle_filled(
    #     arcade.get_window().width / 2,
    #     arcade.get_window().height / 2,
    #     arcade.get_window().width - 100,
    #     arcade.get_window().height - 100,
    #     (10, 10, 20, 240)  # Тёмно-синий полупрозрачный
    # )
    
    # Рамка
    # arcade.draw_lbwh_rectangle_outline(
    #     arcade.get_window().width / 2,
    #     arcade.get_window().height / 2,
    #     arcade.get_window().width - 100,
    #     arcade.get_window().height - 100,
    #     (100, 100, 255),
    #     3
    # )
    
    # Заголовок
    arcade.draw_text(
        "⌨️ УПРАВЛЕНИЕ",
        arcade.get_window().width / 2,
        arcade.get_window().height - 80,
        arcade.color.GOLD,
        28,
        anchor_x="center",
        anchor_y="top",
        font_name="Arial",
        bold=True
    )
    
    # Рисуем все секции
    y_offset = arcade.get_window().height - 130
    for section_title, controls in CONTROLS:
        # Заголовок секции
        arcade.draw_text(
            section_title,
        50,
            y_offset,
            arcade.color.CYAN,
            16,
            font_name="Arial",
            bold=True
        )
        y_offset -= 30
        
        # Элементы управления
        for key, description in controls:
            # Клавиша
            arcade.draw_text(
                key,
                70,
                y_offset,
                arcade.color.YELLOW,
                13,
                font_name="Arial",
                bold=True,
                width=150,
                align="right"
            )
            # Описание
            arcade.draw_text(
                description,
                230,
                y_offset,
                arcade.color.LIGHT_GRAY,
                13,
                font_name="Arial"
            )
            y_offset -= 25
        
        y_offset -= 10  # Отступ между секциями
    
    # Подсказка для закрытия
    arcade.draw_text(
        "Нажмите F1 или H чтобы закрыть",
        arcade.get_window().width / 2,
        50,
        arcade.color.WHITE,
        14,
        anchor_x="center",
        font_name="Arial",
        italic=True
    )