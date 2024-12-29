from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
import sqlite3
from datetime import datetime

class StudyPlannerApp(App):
    def build(self):
        return StudyPlanner()

class StudyPlanner(BoxLayout):
    course_input = ObjectProperty(None)
    assignment_input = ObjectProperty(None)
    exam_input = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        # Создание базы данных
        self.conn = sqlite3.connect("study_planner.db")
        self.cursor = self.conn.cursor()
        self.create_tables()

        # Создание интерфейса
        self.create_ui()

    def create_tables(self):
        """Создание таблиц базы данных"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER,
                name TEXT,
                due_date TEXT,
                FOREIGN KEY (course_id) REFERENCES courses (id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS exams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER,
                name TEXT,
                exam_date TEXT,
                FOREIGN KEY (course_id) REFERENCES courses (id)
            )
        """)
        self.conn.commit()

    def create_ui(self):
        """Создание интерфейса"""
        # Поля ввода для курсов
        self.course_input = TextInput(hint_text="Название курса", multiline=False)
        self.add_widget(self.course_input)
        self.add_course_button = Button(text="Добавить курс", on_press=self.add_course)
        self.add_widget(self.add_course_button)

        # Поля ввода для заданий
        self.assignment_input = TextInput(hint_text="Название задания", multiline=False)
        self.due_date_input = TextInput(hint_text="Дата сдачи (гггг-мм-дд)", multiline=False)
        self.course_spinner = Spinner(text="Выберите курс", values=self.get_courses())
        self.add_widget(self.assignment_input)
        self.add_widget(self.due_date_input)
        self.add_widget(self.course_spinner)
        self.add_assignment_button = Button(text="Добавить задание", on_press=self.add_assignment)
        self.add_widget(self.add_assignment_button)

        # Поля ввода для экзаменов
        self.exam_input = TextInput(hint_text="Название экзамена", multiline=False)
        self.exam_date_input = TextInput(hint_text="Дата экзамена (гггг-мм-дд)", multiline=False)
        self.add_widget(self.exam_input)
        self.add_widget(self.exam_date_input)
        self.add_exam_button = Button(text="Добавить экзамен", on_press=self.add_exam)
        self.add_widget(self.add_exam_button)

        # Кнопки для просмотра
        self.show_courses_button = Button(text="Показать курсы", on_press=self.show_courses)
        self.show_assignments_button = Button(text="Показать задания", on_press=self.show_assignments)
        self.show_exams_button = Button(text="Показать экзамены", on_press=self.show_exams)
        self.add_widget(self.show_courses_button)
        self.add_widget(self.show_assignments_button)
        self.add_widget(self.show_exams_button)

    def get_courses(self):
        """Получение списка курсов из базы данных"""
        self.cursor.execute("SELECT name FROM courses")
        return [row[0] for row in self.cursor.fetchall()]

    def add_course(self, instance):
        """Добавление курса в базу данных"""
        course_name = self.course_input.text
        if not course_name:
            self.show_popup("Ошибка", "Название курса не может быть пустым!")
            return
        try:
            self.cursor.execute("INSERT INTO courses (name) VALUES (?)", (course_name,))
            self.conn.commit()
            self.show_popup("Успех", "Курс добавлен!")
            self.course_spinner.values = self.get_courses()
        except sqlite3.IntegrityError:
            self.show_popup("Ошибка", "Курс с таким названием уже существует!")

    def add_assignment(self, instance):
        """Добавление задания в базу данных"""
        assignment_name = self.assignment_input.text
        due_date = self.due_date_input.text
        course_name = self.course_spinner.text

        if not assignment_name or not due_date or course_name == "Выберите курс":
            self.show_popup("Ошибка", "Заполните все поля!")
            return

        try:
            datetime.strptime(due_date, "%Y-%m-%d")
            self.cursor.execute("SELECT id FROM courses WHERE name = ?", (course_name,))
            course_id = self.cursor.fetchone()
            if course_id:
                self.cursor.execute("""
                    INSERT INTO assignments (course_id, name, due_date)
                    VALUES (?, ?, ?)
                """, (course_id[0], assignment_name, due_date))
                self.conn.commit()
                self.show_popup("Успех", "Задание добавлено!")
            else:
                self.show_popup("Ошибка", "Выбранный курс не существует!")
        except ValueError:
            self.show_popup("Ошибка", "Дата должна быть в формате гггг-мм-дд!")

    def add_exam(self, instance):
        """Добавление экзамена в базу данных"""
        exam_name = self.exam_input.text
        exam_date = self.exam_date_input.text
        course_name = self.course_spinner.text

        if not exam_name or not exam_date or course_name == "Выберите курс":
            self.show_popup("Ошибка", "Заполните все поля!")
            return

        try:
            datetime.strptime(exam_date, "%Y-%m-%d")
            self.cursor.execute("SELECT id FROM courses WHERE name = ?", (course_name,))
            course_id = self.cursor.fetchone()
            if course_id:
                self.cursor.execute("""
                    INSERT INTO exams (course_id, name, exam_date)
                    VALUES (?, ?, ?)
                """, (course_id[0], exam_name, exam_date))
                self.conn.commit()
                self.show_popup("Успех", "Экзамен добавлен!")
            else:
                self.show_popup("Ошибка", "Выбранный курс не существует!")
        except ValueError:
            self.show_popup("Ошибка", "Дата должна быть в формате гггг-мм-дд!")

    def show_courses(self, instance):
        """Показ курсов"""
        self.cursor.execute("SELECT * FROM courses")
        rows = self.cursor.fetchall()
        content = BoxLayout(orientation="vertical")
        for row in rows:
            content.add_widget(Label(text=f"{row[1]}"))

        popup = Popup(title="Курсы", content=content, size_hint=(0.8, 0.8))
        popup.open()

    def show_assignments(self, instance):
        """Показ заданий"""
        self.cursor.execute("SELECT assignments.name, assignments.due_date, courses.name FROM assignments JOIN courses ON assignments.course_id = courses.id")
        rows = self.cursor.fetchall()
        content = BoxLayout(orientation="vertical")
        for row in rows:
            content.add_widget(Label(text=f"{row[2]} | {row[0]} | Дата сдачи: {row[1]}"))

        popup = Popup(title="Задания", content=content, size_hint=(0.8, 0.8))
        popup.open()

    def show_exams(self, instance):
        """Показ экзаменов"""
        self.cursor.execute("SELECT exams.name, exams.exam_date, courses.name FROM exams JOIN courses ON exams.course_id = courses.id")
        rows = self.cursor.fetchall()
        content = BoxLayout(orientation="vertical")
        for row in rows:
            content.add_widget(Label(text=f"{row[2]} | {row[0]} | Дата экзамена: {row[1]}"))

        popup = Popup(title="Экзамены", content=content, size_hint=(0.8, 0.8))
        popup.open()

    def show_popup(self, title, message):
        """Показ всплывающего окна"""
        popup_content = BoxLayout(orientation="vertical")
        popup_content.add_widget(Label(text=message))
        close_button = Button(text="Закрыть", on_press=lambda x: popup.dismiss())
        popup_content.add_widget(close_button)

        popup = Popup(title=title, content=popup_content, size_hint=(0.8, 0.4))
        popup.open()

if __name__ == "__main__":
    StudyPlannerApp().run()
