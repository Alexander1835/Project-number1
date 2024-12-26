from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from matplotlib.figure import Figure
import sqlite3
from datetime import datetime


class FinanceTrackerApp(App):
    def build(self):
        return FinanceTracker()


class FinanceTracker(BoxLayout):
    date_input = ObjectProperty(None)
    amount_input = ObjectProperty(None)
    description_input = ObjectProperty(None)
    type_spinner = ObjectProperty(None)
    category_spinner = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        # Создание базы данных
        self.conn = sqlite3.connect("finance.db")
        self.cursor = self.conn.cursor()
        self.create_tables()

        # Интерфейс
        self.create_ui()

    def create_tables(self):
        """Создание таблиц базы данных"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                amount REAL,
                type TEXT,
                category TEXT,
                description TEXT
            )
        """)
        self.conn.commit()

        # Добавление стандартных категорий
        default_categories = ["Еда", "Транспорт", "Развлечения", "Зарплата", "Подарки"]
        for category in default_categories:
            try:
                self.cursor.execute("INSERT INTO categories (name) VALUES (?)", (category,))
            except sqlite3.IntegrityError:
                pass
        self.conn.commit()

    def create_ui(self):
        """Создание интерфейса"""
        # Поля ввода
        self.date_input = TextInput(hint_text="Дата (гггг-мм-дд)", multiline=False)
        self.amount_input = TextInput(hint_text="Сумма", multiline=False, input_filter="float")
        self.description_input = TextInput(hint_text="Описание", multiline=False)
        self.type_spinner = Spinner(text="Тип", values=["Доход", "Расход"])
        self.category_spinner = Spinner(text="Категория", values=self.get_categories())

        self.add_widget(self.date_input)
        self.add_widget(self.amount_input)
        self.add_widget(self.description_input)
        self.add_widget(self.type_spinner)
        self.add_widget(self.category_spinner)

        # Кнопки
        self.add_button = Button(text="Добавить транзакцию", on_press=self.add_transaction)
        self.show_button = Button(text="Показать транзакции", on_press=self.show_transactions)
        self.chart_button = Button(text="Построить график", on_press=self.show_chart)

        self.add_widget(self.add_button)
        self.add_widget(self.show_button)
        self.add_widget(self.chart_button)

    def get_categories(self):
        """Получение списка категорий из базы данных"""
        self.cursor.execute("SELECT name FROM categories")
        return [row[0] for row in self.cursor.fetchall()]

    def add_transaction(self, instance):
        """Добавление транзакции в базу данных"""
        date = self.date_input.text
        amount = self.amount_input.text
        transaction_type = self.type_spinner.text
        category = self.category_spinner.text
        description = self.description_input.text

        # Проверка на заполненность
        if not date or not amount or not category or transaction_type == "Тип":
            self.show_popup("Ошибка", "Все поля должны быть заполнены!")
            return

        try:
            # Проверка формата даты
            datetime.strptime(date, "%Y-%m-%d")
            self.cursor.execute("""
                INSERT INTO transactions (date, amount, type, category, description)
                VALUES (?, ?, ?, ?, ?)
            """, (date, float(amount), transaction_type, category, description))
            self.conn.commit()
            self.show_popup("Успех", "Транзакция добавлена!")
        except ValueError:
            self.show_popup("Ошибка", "Дата должна быть в формате гггг-мм-дд!")

    def show_transactions(self, instance):
        """Показ всех транзакций"""
        self.cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
        rows = self.cursor.fetchall()

        # Создание всплывающего окна
        content = BoxLayout(orientation="vertical")
        for row in rows:
            content.add_widget(Label(text=f"{row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}"))

        close_button = Button(text="Закрыть", size_hint_y=0.2, on_press=lambda x: popup.dismiss())
        content.add_widget(close_button)

        popup = Popup(title="Транзакции", content=content, size_hint=(0.9, 0.9))
        popup.open()

    def show_chart(self, instance):
        """Отображение графика расходов по категориям"""
        self.cursor.execute("""
            SELECT category, SUM(amount)
            FROM transactions
            WHERE type = 'Расход'
            GROUP BY category
        """)
        data = self.cursor.fetchall()

        if not data:
            self.show_popup("Ошибка", "Нет данных для построения графика!")
            return

        # Построение графика
        categories = [row[0] for row in data]
        amounts = [row[1] for row in data]

        figure = Figure(figsize=(5, 5))
        ax = figure.add_subplot(111)
        ax.pie(amounts, labels=categories, autopct="%1.1f%%")
        ax.set_title("Расходы по категориям")

        popup_content = BoxLayout(orientation="vertical")
        popup_content.add_widget(FigureCanvasKivyAgg(figure))
        close_button = Button(text="Закрыть", size_hint_y=0.2, on_press=lambda x: popup.dismiss())
        popup_content.add_widget(close_button)

        popup = Popup(title="График расходов", content=popup_content, size_hint=(0.9, 0.9))
        popup.open()

    def show_popup(self, title, message):
        """Показывает всплывающее окно с сообщением"""
        popup_content = BoxLayout(orientation="vertical")
        popup_content.add_widget(Label(text=message))
        close_button = Button(text="Закрыть", size_hint_y=0.2, on_press=lambda x: popup.dismiss())
        popup_content.add_widget(close_button)

        popup = Popup(title=title, content=popup_content, size_hint=(0.8, 0.4))
        popup.open()


if __name__ == "__main__":
    FinanceTrackerApp().run()
