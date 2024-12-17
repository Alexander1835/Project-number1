from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.recycleview import RecycleView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from datetime import datetime, timedelta
import sqlite3


class TaskRecycleView(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []


class TaskManagerApp(App):
    def build(self):
        # Подключение к базе данных
        self.conn = sqlite3.connect("tasks.db")
        self.cursor = self.conn.cursor()
        self.create_tables()

        # Основной макет
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Поля ввода
        self.task_input = TextInput(hint_text="Название задачи", multiline=False)
        self.desc_input = TextInput(hint_text="Описание задачи", multiline=True)
        self.priority_spinner = Spinner(
            text="Приоритет",
            values=["Низкий", "Средний", "Высокий"]
        )
        self.category_input = TextInput(hint_text="Категория задачи", multiline=False)
        self.date_input = TextInput(hint_text="Дата окончания (гггг-мм-дд)", multiline=False)

        # Кнопка добавления задачи
        add_task_btn = Button(text="Добавить задачу", size_hint=(1, 0.2), on_press=self.add_task)

        # Список задач с использованием RecycleView
        self.task_list = TaskRecycleView()

        # Добавляем виджеты в макет
        root.add_widget(self.task_input)
        root.add_widget(self.desc_input)
        root.add_widget(self.priority_spinner)
        root.add_widget(self.category_input)
        root.add_widget(self.date_input)
        root.add_widget(add_task_btn)
        root.add_widget(self.task_list)

        # Запуск проверки дедлайнов
        Clock.schedule_interval(self.check_deadlines, 60)  # Проверка каждую минуту
        self.update_task_list()  # Загрузка задач в начале работы приложения
        return root

    def create_tables(self):
        """Создание таблиц для задач и категорий"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                priority TEXT,
                due_date TEXT,
                category TEXT
            )
        """)
        self.conn.commit()

    def add_task(self, instance):
        """Добавление новой задачи в базу данных"""
        title = self.task_input.text.strip()
        description = self.desc_input.text.strip()
        priority = self.priority_spinner.text
        category = self.category_input.text.strip()
        due_date = self.date_input.text.strip()

        if title and priority != "Приоритет" and due_date:
            try:
                # Проверка корректности даты
                datetime.strptime(due_date, "%Y-%m-%d")

                # Добавляем задачу в базу данных
                self.cursor.execute("""
                    INSERT INTO tasks (title, description, priority, due_date, category)
                    VALUES (?, ?, ?, ?, ?)
                """, (title, description, priority, due_date, category))
                self.conn.commit()

                # Очищаем поля ввода
                self.task_input.text = ""
                self.desc_input.text = ""
                self.priority_spinner.text = "Приоритет"
                self.category_input.text = ""
                self.date_input.text = ""

                # Обновляем список задач
                self.update_task_list()

            except ValueError:
                self.show_popup("Ошибка", "Неверный формат даты. Используйте формат гггг-мм-дд.")
        else:
            self.show_popup("Ошибка", "Заполните все поля корректно!")

    def update_task_list(self):
        """Обновление списка задач"""
        self.cursor.execute("SELECT title, priority, due_date FROM tasks")
        tasks = self.cursor.fetchall()
        self.task_list.data = [
            {"text": f"{task[0]} | Приоритет: {task[1]} | Дедлайн: {task[2]}"}
            for task in tasks
        ]

    def check_deadlines(self, dt):
        """Проверка приближающихся сроков выполнения задач"""
        now = datetime.now()
        self.cursor.execute("SELECT title, due_date FROM tasks")
        for title, due_date in self.cursor.fetchall():
            try:
                task_date = datetime.strptime(due_date, "%Y-%m-%d")
                if now >= task_date - timedelta(minutes=1):
                    self.show_popup("Напоминание", f"Срок задачи '{title}' подходит к концу!")
            except ValueError:
                continue  # Игнорируем некорректные даты

    def show_popup(self, title, message):
        """Отображение всплывающего окна с сообщением"""
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.6, 0.4)
        )
        popup.open()

    def on_stop(self):
        """Закрытие соединения с базой данных при завершении приложения"""
        self.conn.close()


if __name__ == "__main__":
    TaskManagerApp().run()
