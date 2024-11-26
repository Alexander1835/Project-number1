from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.uix.label import Label

class SwipeWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rect = Rectangle(size=(100, 100), pos=self.center)
        self.label = Label(text="Смахни меня", center=self.center)
        self.add_widget(self.label)

    def on_touch_move(self, touch):
        if touch.is_mouse_scrolling:
            return

        if touch.dx < 0:  # Смахивание влево
            self.rect.pos = (self.rect.pos[0] - 10, self.rect.pos[1])
            self.label.text = "Смахивание влево"
        elif touch.dx > 0:  # Смахивание вправо
            self.rect.pos = (self.rect.pos[0] + 10, self.rect.pos[1])
            self.label.text = "Смахивание вправо"

    def on_touch_up(self, touch):
        # Сброс текста при отпускании
        self.label.text = "Смахни меня"

class SwipeApp(App):
    def build(self):
        return SwipeWidget()

if __name__ == '__main__':
    SwipeApp().run()
