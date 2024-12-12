from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import sqlite3

# Класс для работы с базой данных пользователей
class UserDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('users.db')
        self.create_table()

    def create_table(self):
        """Создает таблицу пользователей, если она еще не существует."""
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT,
                                age INTEGER,
                                email TEXT)''')

    def add_user(self, name, age, email):
        """Добавляет нового пользователя в базу данных."""
        with self.conn:
            self.conn.execute("INSERT INTO users (name, age, email) VALUES (?, ?, ?)",
                              (name, age, email))

    def edit_user(self, user_id, name, age, email):
        """Редактирует информацию о пользователе по его ID."""
        with self.conn:
            self.conn.execute("UPDATE users SET name = ?, age = ?, email = ? WHERE id = ?",
                              (name, age, email, user_id))

    def delete_user(self, user_id):
        """Удаляет пользователя по его ID."""
        with self.conn:
            self.conn.execute("DELETE FROM users WHERE id = ?", (user_id,))

    def get_users(self):
        """Возвращает список всех пользователей."""
        cursor = self.conn.execute("SELECT * FROM users")
        return cursor.fetchall()

# Виджет для управления профилями пользователей
class UserProfileWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.db = UserDatabase()

        # Ввод для имени пользователя
        self.name_input = TextInput(hint_text='Имя пользователя')
        self.add_widget(self.name_input)

        # Ввод для возраста пользователя
        self.age_input = TextInput(hint_text='Возраст')
        self.add_widget(self.age_input)

        # Ввод для email пользователя
        self.email_input = TextInput(hint_text='Email')
        self.add_widget(self.email_input)

        # Кнопка для добавления пользователя
        add_button = Button(text='Добавить')
        add_button.bind(on_press=self.add_user)
        self.add_widget(add_button)

        # Кнопка для редактирования пользователя
        edit_button = Button(text='Редактировать')
        edit_button.bind(on_press=self.edit_user)
        self.add_widget(edit_button)

        # Кнопка для удаления пользователя
        delete_button = Button(text='Удалить')
        delete_button.bind(on_press=self.delete_user)
        self.add_widget(delete_button)

        # Метка для отображения списка пользователей
        self.user_list = Label()
        self.add_widget(self.user_list)
        self.update_user_list()

    def add_user(self, instance):
        """Добавление нового пользователя"""
        name = self.name_input.text
        age = int(self.age_input.text)
        email = self.email_input.text
        self.db.add_user(name, age, email)
        self.update_user_list()

    def edit_user(self, instance):
        """Редактирование пользователя"""
        # Здесь предполагается, что пользователь вводит ID для редактирования
        user_id = int(self.name_input.text)  # Предположительно, ID пользователя в имени
        name = self.name_input.text
        age = int(self.age_input.text)
        email = self.email_input.text
        self.db.edit_user(user_id, name, age, email)
        self.update_user_list()

    def delete_user(self, instance):
        """Удаление пользователя"""
        user_id = int(self.name_input.text)  # Предположительно, ID пользователя в имени
        self.db.delete_user(user_id)
        self.update_user_list()

    def update_user_list(self):
        """Обновляет отображаемый список пользователей"""
        users = self.db.get_users()
        user_list_text = '\n'.join([f'ID: {u[0]}, Имя: {u[1]}, Возраст: {u[2]}, Email: {u[3]}' for u in users])
        self.user_list.text = user_list_text

# Основное приложение
class UserProfileApp(App):
    def build(self):
        return UserProfileWidget()

if __name__ == '__main__':
    UserProfileApp().run()
