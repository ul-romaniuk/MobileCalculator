from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label

from ui import icons
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
    """Кнопка меню з трьома крапками (згладжені кружечки)."""

    DOT = dp(5)
    GAP = dp(7)

    def __init__(self, style: ButtonStyle, **kwargs):
        super().__init__(style, **kwargs)

        with self.canvas.after:
            self._dots_color = Color(*style.foreground)
            self._dots = [Rectangle() for _ in range(3)]

        self.bind(pos=self._update_dots, size=self._update_dots)
        self._update_dots()

    def apply_style(self, style: ButtonStyle):
        super().apply_style(style)
        self._dots_color.rgba = style.foreground

    def _update_dots(self, *_):
        size = icons.even_size(self.DOT + 2)
        texture = icons.disc(size)
        step = self.DOT + self.GAP

        for index, dot in enumerate(self._dots):
            dot.texture = texture
            dot.size = (size, size)
            dot.pos = (
                round(self.center_x - size / 2),
                round(self.center_y + (1 - index) * step - size / 2),
            )


class ExpandButton(RoundedButton):
    """Кнопка розкриття додаткових функцій: два квадрати і дві стрілки.

    Значок згладжений (див. ui/icons.py) і бере колір зі стилю кнопки.
    """

    def __init__(self, style: ButtonStyle, **kwargs):
        super().__init__(style, **kwargs)

        with self.canvas.after:
            self._icon_color = Color(*style.foreground)
            self._icon = Rectangle()

        self.bind(pos=self._update_icon, size=self._update_icon)
        self._update_icon()

    def apply_style(self, style: ButtonStyle):
        super().apply_style(style)
        self._icon_color.rgba = style.foreground

    def _update_icon(self, *_):
        size = icons.even_size(min(self.width, self.height) * 0.6)

        self._icon.texture = icons.expand_icon(size)
        self._icon.size = (size, size)
        self._icon.pos = (round(self.center_x - size / 2), round(self.center_y - size / 2))


class ChoiceButton(RoundedButton):
    """Рядок меню вибору: текст ліворуч, індикатор праворуч.

    Вибраний варіант позначається заповненим кружечком, невибраний порожнім.
    """

    RADIUS = dp(10)
    EDGE = dp(26)  # відстань від правого краю до центра кружечка

    def __init__(self, style: ButtonStyle, **kwargs):
        super().__init__(style, **kwargs)
        self._selected = False

        with self.canvas.after:
            self._mark_color = Color(0, 0, 0, 0)
            self._mark = Rectangle()

        self.bind(pos=self._update_mark, size=self._update_mark)
        self._update_mark()

    def set_indicator(self, selected, active_color, inactive_color):
        """Заповнений кружечок для вибраного варіанта, порожній для решти."""
        self._selected = selected
        self._mark_color.rgba = active_color if selected else inactive_color
        self._update_mark()

    def _update_mark(self, *_):
        size = icons.even_size(2 * self.RADIUS)

        self._mark.texture = icons.disc(size) if self._selected else icons.ring(size)
        self._mark.size = (size, size)
        self._mark.pos = (
            round(self.right - self.EDGE - size / 2),
            round(self.center_y - size / 2),
        )


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


class MenuOverlay(FloatLayout):
    """Основа меню в правому верхньому куті: затемнення екрана і панель із рядками.

    Дотик поза панеллю закриває меню.
    """

    WIDTH = dp(230)
    ROW_HEIGHT = dp(52)
    PADDING = dp(8)
    MARGIN = dp(16)

    def __init__(self, theme, row_count, dismiss_callback, **kwargs):
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
            size=(self.WIDTH, row_count * self.ROW_HEIGHT + 2 * self.PADDING),
            padding=self.PADDING,
        )
        self.add_widget(self.panel)
        self.bind(pos=self._place_panel, size=self._place_panel)

    @staticmethod
    def _align_text(button, size):
        button.text_size = (size[0] - dp(24), size[1])

    def _place_panel(self, *_):
        self.panel.right = self.x + self.width - self.MARGIN
        self.panel.top = self.y + self.height - self.MARGIN


class PopupMenu(MenuOverlay):
    """Головне меню: список пунктів.

    items - список пар (текст, функція). Після вибору меню закривається.
    """

    def __init__(self, theme, items, dismiss_callback, **kwargs):
        super().__init__(theme, len(items), dismiss_callback, **kwargs)
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

    @staticmethod
    def _choose(action, dismiss_callback):
        dismiss_callback()  # спочатку закриваємо меню, потім виконуємо дію
        action()


class ChoiceMenu(MenuOverlay):
    """Меню вибору одного варіанта (наприклад, теми).

    Біля вибраного варіанта стоїть заповнений кружечок, біля решти порожній.
    Меню лишається відкритим після вибору, а індикатор оновлюється.
    """

    def __init__(self, theme, options, selected, select_callback, dismiss_callback, **kwargs):
        super().__init__(theme, len(options), dismiss_callback, **kwargs)
        self._rows = {}

        for value, text in options:
            row = ChoiceButton(
                ButtonStyle(theme.surface, theme.text),
                text=text,
                font_size=sp(18),
                bold=False,
                halign="left",
                valign="middle",
            )
            row.bind(size=self._align_text)
            row.bind(on_release=lambda _button, v=value: select_callback(v))
            self.panel.add_widget(row)
            self._rows[value] = row

        self.apply_theme(theme, selected)

    def apply_theme(self, theme, selected):
        """Оновлює кольори меню та позначає вибраний варіант."""
        self.panel.set_color(theme.surface)
        accent = theme.button_styles["operator"].background

        for value, row in self._rows.items():
            row.apply_style(ButtonStyle(theme.surface, theme.text))
            row.set_indicator(value == selected, accent, theme.text_muted)


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