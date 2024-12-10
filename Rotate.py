from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.properties import NumericProperty


class RotateWidget(Widget):
    angle = NumericProperty(0)  # Текущий угол поворота виджета

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self.color = Color(0.5, 0.7, 0.9, 1)  # Цвет фона
            self.rect = Rectangle(size=self.size, pos=self.pos)  # Прямоугольник

        # Привязываем обновление позиции и размера прямоугольника к изменениям размеров виджета
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        """Обновляет размер и позицию прямоугольника при изменении размеров виджета"""
        self.rect.size = self.size
        self.rect.pos = self.pos

    def on_touch_down(self, touch):
        """Обрабатывает касания: добавляем начальный угол поворота"""
        if len(touch.ud) == 0:
            touch.ud['angle'] = self.angle  # Сохраняем текущий угол поворота в словарь касания
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        """Обрабатывает движение касаний: изменяем угол поворота при жесте "пинч"."""
        if len(touch.ud) == 0:  # Если касание не связано с другими
            if len(self.get_active_touches()) == 2:  # Проверяем, есть ли два пальца
                touch1, touch2 = self.get_active_touches()  # Два активных касания
                # Вычисляем угловое расстояние между пальцами
                angle1 = touch1.angle
                angle2 = touch2.angle
                # Определяем угол вращения
                delta_angle = angle2 - angle1
                self.angle = touch.ud['angle'] + delta_angle
                self.apply_rotation()

    def apply_rotation(self):
        """Применяет вращение виджета."""
        self.canvas.ask_update()  # Обновляем отображение виджета

    def get_active_touches(self):
        """Получает все активные касания для текущего виджета."""
        return [t for t in self.get_parent_window().touches if self.collide_point(*t.pos)]


class RotateApp(App):
    def build(self):
        # Создаем виджет и задаем ему начальные размеры и положение
        root = Widget()
        rotate_widget = RotateWidget(size=(200, 200), pos=(100, 100))
        root.add_widget(rotate_widget)
        return root


if __name__ == '__main__':
    RotateApp().run()
