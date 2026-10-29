"""Kivy-подання з відомостями про застосунок."""

from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from config import settings
from ui.widgets import RoundedButton, SurfacePanel


class WrappedLabel(Label):
    """Напис, який переносить текст на новий рядок і підлаштовує свою висоту."""

    def __init__(self, **kwargs):
        """Створює напис, висота якого залежить від перенесеного тексту."""
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "top")
        super().__init__(size_hint_y=None, **kwargs)
        self.bind(width=self._wrap, texture_size=self._fit_height)

    def _wrap(self, *_):
        self.text_size = (self.width, None)

    def _fit_height(self, *_):
        self.height = self.texture_size[1]


class AboutScreen(Screen):
    """Екран з відомостями про застосунок і розробника."""

    def __init__(self, theme, back_callback, **kwargs):
        """Створює екран відомостей із темою та дією повернення."""
        super().__init__(**kwargs)
        self.theme = theme
        self.back_callback = back_callback

        layout = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        bar = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(16))
        self.back_button = RoundedButton(
            theme.button_styles["secondary"],
            text="Назад",
            font_size=sp(16),
            size_hint_x=None,
            width=dp(110),
        )
        self.back_button.bind(on_release=lambda _button: self.back_callback())

        self.title_label = Label(
            text="Про розробника",
            font_size=sp(22),
            bold=True,
            halign="left",
            valign="middle",
        )
        self.title_label.bind(size=lambda label, size: setattr(label, "text_size", size))

        bar.add_widget(self.back_button)
        bar.add_widget(self.title_label)

        self.panel = SurfacePanel(
            theme.surface,
            orientation="vertical",
            size_hint_y=None,
            padding=dp(20),
            spacing=dp(14),
        )
        self.panel.bind(minimum_height=self.panel.setter("height"))

        self.captions = []
        self.values = []

        for caption, value in settings.about_info:
            row = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(2))
            row.bind(minimum_height=row.setter("height"))

            caption_label = WrappedLabel(text=caption, font_size=sp(14))
            value_label = WrappedLabel(text=value, font_size=sp(18))

            row.add_widget(caption_label)
            row.add_widget(value_label)
            self.panel.add_widget(row)
            self.captions.append(caption_label)
            self.values.append(value_label)

        scroll = ScrollView()
        scroll.add_widget(self.panel)

        layout.add_widget(bar)
        layout.add_widget(scroll)
        self.add_widget(layout)

        self.apply_theme(theme)

    def apply_theme(self, theme):
        """Застосовує тему до всіх елементів екрана."""
        self.theme = theme
        self.back_button.apply_style(theme.button_styles["secondary"])
        self.title_label.color = theme.text
        self.panel.set_color(theme.surface)

        for label in self.captions:
            label.color = theme.text_muted

        for label in self.values:
            label.color = theme.text
