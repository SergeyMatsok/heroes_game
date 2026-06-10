import arcade
import random

class FloatingText:
    """Летящее число урона"""
    def __init__(self, text, x, y, color, size=24):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.life = 60  # 60 кадров = 1 секунда
        self.max_life = 60
        self.velocity_y = 2  # Скорость подъёма
    
    def update(self):
        self.y += self.velocity_y
        self.velocity_y *= 0.95  # Замедление
        self.life -= 1
        return self.life > 0
    
    def draw(self):
        alpha = int(255 * (self.life / self.max_life))
        color_with_alpha = (*self.color[:3], alpha)
        arcade.draw_text(
            self.text,
            self.x, self.y,
            color_with_alpha,
            self.size,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial",
            bold=True
        )


class DamageFlash:
    """Вспышка при ударе"""
    def __init__(self, x, y, radius=40):
        self.x = x
        self.y = y
        self.radius = radius
        self.life = 15
        self.max_life = 15
    
    def update(self):
        self.life -= 1
        return self.life > 0
    
    def draw(self):
        alpha = int(200 * (self.life / self.max_life))
        current_radius = self.radius * (1 - self.life / self.max_life * 0.5)
        arcade.draw_circle_filled(
            self.x, self.y, current_radius,
            (255, 255, 200, alpha)
        )


class ScreenShake:
    """Тряска экрана"""
    def __init__(self, intensity=5, duration=20):
        self.intensity = intensity
        self.duration = duration
        self.life = duration
        self.offset_x = 0
        self.offset_y = 0
    
    def update(self):
        if self.life > 0:
            self.offset_x = random.uniform(-self.intensity, self.intensity)
            self.offset_y = random.uniform(-self.intensity, self.intensity)
            self.life -= 1
        else:
            self.offset_x = 0
            self.offset_y = 0
        return self.life > 0


class CombatAnimator:
    """Управляет всеми анимациями боя"""
    def __init__(self):
        self.floating_texts = []
        self.flashes = []
        self.shake = None
        self.attack_animation = None  # Текущая анимация атаки
    
    def add_damage(self, x, y, damage, is_critical=False):
        """Добавить летящее число урона"""
        color = (255, 50, 50) if not is_critical else (255, 255, 0)
        size = 28 if not is_critical else 36
        text = f"-{damage}"
        if is_critical:
            text = f"КРИТ! -{damage}"
        self.floating_texts.append(FloatingText(text, x, y, color, size))
    
    def add_heal(self, x, y, amount):
        """Добавить летящее число лечения"""
        self.floating_texts.append(FloatingText(f"+{amount}", x, y, (50, 255, 50), 24))
    
    def add_flash(self, x, y, radius=40):
        """Добавить вспышку"""
        self.flashes.append(DamageFlash(x, y, radius))
    
    def add_shake(self, intensity=5, duration=20):
        """Добавить тряску экрана"""
        self.shake = ScreenShake(intensity, duration)
    
    def update(self):
        """Обновить все анимации"""
        self.floating_texts = [ft for ft in self.floating_texts if ft.update()]
        self.flashes = [f for f in self.flashes if f.update()]
        if self.shake:
            self.shake.update()
    
    def draw(self):
        """Нарисовать все анимации"""
        for ft in self.floating_texts:
            ft.draw()
        for f in self.flashes:
            f.draw()
    
    def get_shake_offset(self):
        """Получить смещение тряски"""
        if self.shake and self.shake.life > 0:
            return self.shake.offset_x, self.shake.offset_y
        return 0, 0