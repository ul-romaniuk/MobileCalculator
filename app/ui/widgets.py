from kivy.graphics import Color, Ellipse, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label

from ui.theme import ButtonStyle, pressed_variant


class RoundedButton(Button):
    """Кнопка із закругленими кутами; кольори беруться зі стилю теми."""

    def __init__(self, style: ButtonStyle, **kwargs):
        kwargs.setdefault("bold", True)
        super().__init__(
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            **kwargs,
        )
        self._normal_color = style.background
        self._pressed_color = pressed_variant(style.background)
        self.color = style.foreground

        with self.canvas.before:
            self._fill = Color(*self._normal_color)
            self._shape = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(20)],
            )

        self.bind(pos=self._update_shape, size=self._update_shape, state=self._update_color)

    def apply_style(self, style: ButtonStyle):
        self._normal_color = style.background
        self._pressed_color = pressed_variant(style.background)
        self.color = style.foreground
        self._update_color()

    def _update_shape(self, *_):
        self._shape.pos = self.pos
        self._shape.size = self.size

    def _update_color(self, *_):
        self._fill.rgba = self._pressed_color if self.state == "down" else self._normal_color


class MenuButton(RoundedButton):
    """Кнопка меню з трьома крапками. Крапки малюються, а не беруться зі шрифту."""

    DOT = dp(5)
    GAP = dp(7)

    def __init__(self, style: ButtonStyle, **kwargs):
        super().__init__(style, **kwargs)

        with self.canvas.after:
            self._dots_color = Color(*style.foreground)
            self._dots = [Ellipse(size=(self.DOT, self.DOT)) for _ in range(3)]

        self.bind(pos=self._update_dots, size=self._update_dots)
        self._update_dots()

    def apply_style(self, style: ButtonStyle):
        super().apply_style(style)
        self._dots_color.rgba = style.foreground

    def _update_dots(self, *_):
        center_x, center_y = self.center
        step = self.DOT + self.GAP

        for index, dot in enumerate(self._dots):
            dot.pos = (center_x - self.DOT / 2, center_y + (1 - index) * step - self.DOT / 2)


class SurfacePanel(BoxLayout):
    """Панель із закругленими кутами (фон меню та екрана з даними)."""

    def __init__(self, color, radius=18, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            self._fill = Color(*color)
            self._shape = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(radius)])

        self.bind(pos=self._update_shape, size=self._update_shape)

    def set_color(self, color):
        self._fill.rgba = color

    def _update_shape(self, *_):
        self._shape.pos = self.pos
        self._shape.size = self.size


class PopupMenu(FloatLayout):
    """Меню в правому верхньому куті: затемнення екрана і список пунктів.

    items - список пар (текст, функція). Дотик поза меню закриває його.
    """

    WIDTH = dp(230)
    ROW_HEIGHT = dp(52)
    PADDING = dp(8)
    MARGIN = dp(16)

    def __init__(self, theme, items, dismiss_callback, **kwargs):
        super().__init__(**kwargs)

        scrim = Button(
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0.35),
        )
        scrim.bind(on_release=lambda _button: dismiss_callback())
        self.add_widget(scrim)

        self.panel = SurfacePanel(
            theme.surface,
            orientation="vertical",
            size_hint=(None, None),
            size=(self.WIDTH, len(items) * self.ROW_HEIGHT + 2 * self.PADDING),
            padding=self.PADDING,
        )
        style = ButtonStyle(theme.surface, theme.text)

        for text, action in items:
            item = RoundedButton(
                style,
                text=text,
                font_size=sp(18),
                bold=False,
                halign="left",
                valign="middle",
            )
            item.bind(size=self._align_text)
            item.bind(on_release=lambda _button, a=action: self._choose(a, dismiss_callback))
            self.panel.add_widget(item)

        self.add_widget(self.panel)
        self.bind(pos=self._place_panel, size=self._place_panel)

    @staticmethod
    def _align_text(button, size):
        button.text_size = (size[0] - dp(24), size[1])

    @staticmethod
    def _choose(action, dismiss_callback):
        dismiss_callback()  # спочатку закриваємо меню, потім виконуємо дію
        action()

    def _place_panel(self, *_):
        self.panel.right = self.x + self.width - self.MARGIN
        self.panel.top = self.y + self.height - self.MARGIN


class DisplayLabel(Label):
    """Дисплей калькулятора з підтримкою довгих повідомлень."""

    def __init__(self, **kwargs):
        kwargs.setdefault("halign", "right")
        kwargs.setdefault("valign", "middle")
        kwargs.setdefault("padding", (dp(8), dp(6)))
        super().__init__(**kwargs)

        self.bind(size=self._update_text_size)

    def _update_text_size(self, *_):
        self.text_size = (
            max(0, self.width - dp(16)),
            max(0, self.height - dp(12)),
        )
