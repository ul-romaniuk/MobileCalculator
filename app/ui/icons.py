"""Згладжені значки для кнопок.

Лінії та кола Kivy малює без згладжування, тому тонкі краї виходять східцями.
Тут форма обчислюється за відстанню до її краю, а крайні пікселі отримують
часткову прозорість. Результат: біла фігура на прозорому тлі. Потрібний колір
задається через Color на canvas кнопки.
"""

import math
from functools import lru_cache

from kivy.graphics.texture import Texture

# Значок розкриття: розміри в одиницях, де 1 дорівнює половині розміру значка
STROKE = 0.16  # товщина ліній
SQUARES = ((-0.62, -0.62), (-0.10, -0.10))  # лівий нижній кут квадратів
SIDE = 0.72  # сторона квадрата
CORNER = 0.20  # радіус закруглення кутів
ARROWS = (((-0.82, 0.38), (-0.46, 0.78)), ((0.82, -0.38), (0.46, -0.78)))  # початок і кінець
HEAD = 0.34  # довжина наконечника стрілки


def even_size(pixels):
    """Розмір текстури в пікселях: ціле парне число, не менше 2."""
    return max(2, int(round(pixels / 2)) * 2)


def _coverage(distance):
    """Яку частку пікселя закриває фігура, якщо до її краю `distance` пікселів."""
    value = 0.5 - distance
    return 0.0 if value < 0.0 else 1.0 if value > 1.0 else value


def _segment_distance(px, py, ax, ay, bx, by):
    abx, aby = bx - ax, by - ay
    t = ((px - ax) * abx + (py - ay) * aby) / (abx * abx + aby * aby)
    t = 0.0 if t < 0.0 else 1.0 if t > 1.0 else t
    return math.hypot(px - (ax + t * abx), py - (ay + t * aby))


def _rounded_box_distance(px, py, cx, cy, half, radius):
    """Відстань зі знаком від точки до краю закругленого квадрата."""
    qx = abs(px - cx) - (half - radius)
    qy = abs(py - cy) - (half - radius)
    outside = math.hypot(max(qx, 0.0), max(qy, 0.0))
    inside = min(max(qx, qy), 0.0)
    return outside + inside - radius


def _paint(alpha, size, bounds, shader):
    """Заповнює прозорість у межах `bounds`; shader(x, y) дає покриття пікселя."""
    left, bottom, right, top = bounds

    for j in range(max(0, int(bottom)), min(size, int(math.ceil(top)) + 1)):
        for i in range(max(0, int(left)), min(size, int(math.ceil(right)) + 1)):
            value = shader(i + 0.5, j + 0.5)
            index = j * size + i

            if value > alpha[index]:
                alpha[index] = value


def _texture(size, alpha):
    data = bytearray(b"\xff" * (size * size * 4))
    data[3::4] = bytes(int(value * 255 + 0.5) for value in alpha)
    data = bytes(data)

    texture = Texture.create(size=(size, size), colorfmt="rgba")
    texture.blit_buffer(data, colorfmt="rgba", bufferfmt="ubyte")
    # після втрати графічного контексту (наприклад, на Android) дані завантажуються знову
    texture.add_reload_observer(
        lambda tex: tex.blit_buffer(data, colorfmt="rgba", bufferfmt="ubyte")
    )

    return texture


@lru_cache(maxsize=None)
def expand_icon(size):
    """Значок розкриття: два квадрати і дві стрілки."""
    unit = size / 2
    half_width = STROKE * unit / 2
    margin = half_width + 2
    alpha = [0.0] * (size * size)

    def to_pixels(x, y):
        return size / 2 + x * unit, size / 2 + y * unit

    for x, y in SQUARES:
        cx, cy = to_pixels(x + SIDE / 2, y + SIDE / 2)
        half = SIDE * unit / 2
        radius = CORNER * unit

        _paint(
            alpha,
            size,
            (cx - half - margin, cy - half - margin, cx + half + margin, cy + half + margin),
            lambda px, py: _coverage(
                abs(_rounded_box_distance(px, py, cx, cy, half, radius)) - half_width
            ),
        )

    for start, end in ARROWS:
        tail, tip = to_pixels(*start), to_pixels(*end)
        angle = math.atan2(tip[1] - tail[1], tip[0] - tail[0])
        spread = math.radians(40)
        length = HEAD * unit
        segments = [(tail, tip)]

        for sign in (-1, 1):
            head = (
                tip[0] - length * math.cos(angle + sign * spread),
                tip[1] - length * math.sin(angle + sign * spread),
            )
            segments.append((tip, head))

        for (ax, ay), (bx, by) in segments:
            _paint(
                alpha,
                size,
                (min(ax, bx) - margin, min(ay, by) - margin, max(ax, bx) + margin, max(ay, by) + margin),
                lambda px, py: _coverage(_segment_distance(px, py, ax, ay, bx, by) - half_width),
            )

    return _texture(size, alpha)


@lru_cache(maxsize=None)
def ring(size):
    """Порожній кружечок (контур)."""
    half_width = size * 0.08
    radius = size / 2 - half_width - 0.5
    center = size / 2
    alpha = [0.0] * (size * size)

    _paint(
        alpha,
        size,
        (0, 0, size, size),
        lambda px, py: _coverage(abs(math.hypot(px - center, py - center) - radius) - half_width),
    )

    return _texture(size, alpha)


@lru_cache(maxsize=None)
def disc(size):
    """Заповнений кружечок."""
    radius = size / 2 - 0.5
    center = size / 2
    alpha = [0.0] * (size * size)

    _paint(
        alpha,
        size,
        (0, 0, size, size),
        lambda px, py: _coverage(math.hypot(px - center, py - center) - radius),
    )

    return _texture(size, alpha)
