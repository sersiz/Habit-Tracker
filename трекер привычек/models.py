import sqlite3
from datetime import datetime, timedelta


class HabitModel:
    def __init__(self):
        self.conn = sqlite3.connect("habit_tracker.db")
        self.create_tables()

    def create_tables(self):
        # Создание таблиц для привычек и выполнений
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS habits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    frequency TEXT NOT NULL
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS completions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    habit_id INTEGER,
                    completion_date TEXT NOT NULL,
                    FOREIGN KEY (habit_id) REFERENCES habits (id)
                )
            """)

    def add_habit(self, name, description, frequency):
        # Добавление новой привычки
        with self.conn:
            cursor = self.conn.execute(
                "INSERT INTO habits (name, description, frequency) VALUES (?, ?, ?)",
                (name, description, frequency)
            )
            return cursor.lastrowid

    def get_habits(self):
        # Получение всех привычек
        cursor = self.conn.execute("SELECT id, name, description, frequency FROM habits")
        return cursor.fetchall()

    def update_habit(self, habit_id, name, description, frequency):
        # Обновление существующей привычки
        with self.conn:
            self.conn.execute(
                "UPDATE habits SET name = ?, description = ?, frequency = ? WHERE id = ?",
                (name, description, frequency, habit_id)
            )

    def delete_habit(self, habit_id):
        # Удаление привычки и ее выполнений
        with self.conn:
            self.conn.execute("DELETE FROM completions WHERE habit_id = ?", (habit_id,))
            self.conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))

    def mark_completion(self, habit_id, date):
        # Отметка выполнения привычки на указанную дату
        with self.conn:
            self.conn.execute(
                "INSERT INTO completions (habit_id, completion_date) VALUES (?, ?)",
                (habit_id, date)
            )

    def unmark_completion(self, habit_id, date):
        # Снятие отметки выполнения на указанную дату
        with self.conn:
            self.conn.execute(
                "DELETE FROM completions WHERE habit_id = ? AND completion_date = ?",
                (habit_id, date)
            )

    def get_completions(self, habit_id, start_date, end_date):
        # Получение выполнений для привычки в диапазоне дат
        cursor = self.conn.execute(
            "SELECT completion_date FROM completions WHERE habit_id = ? AND completion_date BETWEEN ? AND ?",
            (habit_id, start_date, end_date)
        )
        return [row[0] for row in cursor.fetchall()]

    def get_streak(self, habit_id, frequency):
        # Расчет стриков
        today = datetime.now()
        if frequency == "Ежедневно":
            start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        else:  # Еженедельно
            start_date = (today - timedelta(days=90)).strftime("%Y-%m-%d")

        completions = self.get_completions(habit_id, start_date, today.strftime("%Y-%m-%d"))
        completions = sorted(completions, reverse=True)

        streak = 0
        current = today
        while completions:
            if current.strftime("%Y-%m-%d") in completions:
                streak += 1
                completions.pop(0)
                current -= timedelta(days=1 if frequency == "Ежедневно" else 7)
            else:
                break
        return streak

    def __del__(self):
        self.conn.close()