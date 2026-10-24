from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.utils import get_hex_from_color

from storage.history import History
from ui.widgets import RoundedButton


class HistoryScreen(Screen):
    """Екран зі списком останніх обчислень. Дотик до запису повертає його вираз."""

    def __init__(self, history: History, theme, back_callback, select_callback, **kwargs):
        super().__init__(**kwargs)
        self.history = history
        self.theme = theme
        self.back_callback = back_callback
        self.select_callback = select_callback

        layout = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        bar = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(12))
        self.back_button = RoundedButton(
            theme.button_styles["secondary"],
            text="Назад",
            font_size=sp(16),
            size_hint_x=None,
            width=dp(110),
        )
        self.back_button.bind(on_release=lambda _button: self.back_callback())

        self.title_label = Label(text="Історія", font_size=sp(22), bold=True)

        self.clear_button = RoundedButton(
            theme.button_styles["secondary"],
            text="Очистити",
            font_size=sp(16),
            size_hint_x=None,
            width=dp(110),
        )
        self.clear_button.bind(on_release=lambda _button: self._clear_history())

        bar.add_widget(self.back_button)
        bar.add_widget(self.title_label)
        bar.add_widget(self.clear_button)

        self.items = BoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None)
        self.items.bind(minimum_height=self.items.setter("height"))

        scroll = ScrollView()
        scroll.add_widget(self.items)

        layout.add_widget(bar)
        layout.add_widget(scroll)
        self.add_widget(layout)

        self.apply_theme(theme)

    def apply_theme(self, theme):
        self.theme = theme
        self.back_button.apply_style(theme.button_styles["secondary"])
        self.clear_button.apply_style(theme.button_styles["secondary"])
        self.title_label.color = theme.text
        self._rebuild()

    def on_pre_enter(self, *args):
        self._rebuild()

    def _clear_history(self):
        self.history.clear()
        self._rebuild()

    def _rebuild(self):
        self.items.clear_widgets()
        entries = self.history.entries

        if not entries:
            self.items.add_widget(
                Label(
                    text="Історія порожня",
                    font_size=sp(18),
                    color=self.theme.text_muted,
                    size_hint_y=None,
                    height=dp(120),
                )
            )
            return

        muted = get_hex_from_color(self.theme.text_muted)

        for entry in entries:
            text = (
                f"[size={int(sp(15))}][color={muted}]{entry.expression} =[/color][/size]\n"
                f"[b]{entry.result}[/b]"
            )
            item = RoundedButton(
                self.theme.button_styles["number"],
                text=text,
                markup=True,
                bold=False,
                font_size=sp(26),
                halign="right",
                valign="middle",
                size_hint_y=None,
                height=dp(84),
            )
            item.bind(size=lambda widget, _size: setattr(
                widget, "text_size", (widget.width - dp(32), widget.height)
            ))
            item.bind(on_release=lambda _button, e=entry: self.select_callback(e))
            self.items.add_widget(item)