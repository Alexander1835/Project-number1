from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Line
import sqlite3
import matplotlib.pyplot as plt
import csv
import os


class HealthDiaryApp(App):
    def build(self):
        self.conn = sqlite3.connect("health_diary.db")
        self.create_table()
        return DiaryMainLayout(self)

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            weight REAL,
            blood_sugar REAL,
            steps INTEGER
        )
        """)
        self.conn.commit()

    def close_db(self):
        self.conn.close()


class DiaryMainLayout(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.app = app

        # Заголовок
        self.add_widget(Label(text="Дневник здоровья", font_size=24, size_hint=(1, 0.1)))

        # Поля ввода данных
        self.date_input = TextInput(hint_text="Дата (ГГГГ-ММ-ДД)", multiline=False)
        self.weight_input = TextInput(hint_text="Вес (кг)", multiline=False)
        self.blood_sugar_input = TextInput(hint_text="Уровень сахара", multiline=False)
        self.steps_input = TextInput(hint_text="Шаги", multiline=False)
        self.add_widget(self.date_input)
        self.add_widget(self.weight_input)
        self.add_widget(self.blood_sugar_input)
        self.add_widget(self.steps_input)

        # Кнопки
        save_button = Button(text="Сохранить данные")
        save_button.bind(on_press=self.save_data)
        self.add_widget(save_button)

        view_button = Button(text="Посмотреть данные")
        view_button.bind(on_press=self.show_data)
        self.add_widget(view_button)

        export_button = Button(text="Экспорт в CSV")
        export_button.bind(on_press=self.export_to_csv)
        self.add_widget(export_button)

        plot_button = Button(text="Построить графики")
        plot_button.bind(on_press=self.plot_graphs)
        self.add_widget(plot_button)

    def save_data(self, instance):
        """Сохраняет данные в базу"""
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("""
            INSERT INTO health_records (date, weight, blood_sugar, steps)
            VALUES (?, ?, ?, ?)
            """, (
                self.date_input.text,
                float(self.weight_input.text),
                float(self.blood_sugar_input.text),
                int(self.steps_input.text),
            ))
            self.app.conn.commit()
            self.show_popup("Успех", "Данные успешно сохранены!")
        except Exception as e:
            self.show_popup("Ошибка", f"Не удалось сохранить данные: {e}")

    def show_data(self, instance):
        """Отображает данные из базы"""
        cursor = self.app.conn.cursor()
        cursor.execute("SELECT * FROM health_records ORDER BY date DESC")
        records = cursor.fetchall()

        layout = BoxLayout(orientation="vertical", size_hint_y=None)
        layout.bind(minimum_height=layout.setter("height"))

        for record in records:
            layout.add_widget(Label(
                text=f"Дата: {record[1]}, Вес: {record[2]}, Сахар: {record[3]}, Шаги: {record[4]}",
                size_hint_y=None, height=40
            ))

        scrollview = ScrollView(size_hint=(1, 0.8))
        scrollview.add_widget(layout)

        popup = Popup(title="Записи", content=scrollview, size_hint=(0.9, 0.9))
        popup.open()

    def export_to_csv(self, instance):
        """Экспортирует данные в CSV"""
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("SELECT * FROM health_records ORDER BY date DESC")
            records = cursor.fetchall()

            with open("health_diary.csv", "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["ID", "Дата", "Вес", "Сахар", "Шаги"])
                writer.writerows(records)

            self.show_popup("Успех", "Данные экспортированы в health_diary.csv!")
        except Exception as e:
            self.show_popup("Ошибка", f"Не удалось экспортировать данные: {e}")

    def plot_graphs(self, instance):
        """Рисует графики на основе данных"""
        cursor = self.app.conn.cursor()
        cursor.execute("SELECT date, weight, blood_sugar, steps FROM health_records ORDER BY date ASC")
        records = cursor.fetchall()

        if not records:
            self.show_popup("Информация", "Нет данных для отображения.")
            return

        dates, weights, sugars, steps = zip(*records)

        plt.figure(figsize=(10, 6))
        plt.subplot(3, 1, 1)
        plt.plot(dates, weights, label="Вес (кг)", marker="o")
        plt.legend()

        plt.subplot(3, 1, 2)
        plt.plot(dates, sugars, label="Уровень сахара", color="orange", marker="o")
        plt.legend()

        plt.subplot(3, 1, 3)
        plt.plot(dates, steps, label="Шаги", color="green", marker="o")
        plt.legend()

        plt.tight_layout()
        plt.show()

    def show_popup(self, title, message):
        """Показывает всплывающее окно"""
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.7, 0.5))
        popup.open()


if __name__ == "__main__":
    app = HealthDiaryApp()
    try:
        app.run()
    finally:
        app.close_db()
