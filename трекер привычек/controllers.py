import flet as ft
from datetime import datetime, timedelta


class HabitTrackerController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def setup_view(self):
        # Настройка начального вида
        self.view.setup_page(self.handle_save, self.handle_cancel)
        self.refresh_habit_list()

    def refresh_habit_list(self):
        # Обновление списка привычек
        habits = self.model.get_habits()
        self.view.update_habit_list(habits, self.handle_mark, self.handle_edit, self.handle_delete,
                                    self.handle_show_dates)

    def handle_save(self, e):
        # Обработка действия сохранения для добавления/редактирования
        name = self.view.add_form.controls[0].value
        description = self.view.add_form.controls[1].value
        frequency = self.view.add_form.controls[2].value
        habit_id = self.view.add_form.controls[3].data

        if not name or not frequency:
            self.view.page.add(ft.Text("Название и периодичность обязательны"))
            return

        if habit_id:
            self.model.update_habit(habit_id, name, description, frequency)
        else:
            self.model.add_habit(name, description, frequency)

        self.view.clear_form()
        self.refresh_habit_list()

    def handle_cancel(self, e):
        # Обработка действия отмены
        self.view.clear_form()

    def handle_mark(self, e):
        # Обработка отметки выполнения привычки
        habit_id = e.control.data
        today = datetime.now().strftime("%Y-%m-%d")
        self.model.mark_completion(habit_id, today)
        self.refresh_habit_list()

    def handle_edit(self, e):
        # Обработка действия редактирования
        habit_id = e.control.data
        habits = self.model.get_habits()
        for habit in habits:
            if habit[0] == habit_id:
                self.view.populate_edit_form(habit[0], habit[1], habit[2], habit[3])
                break

    def handle_delete(self, e):
        # Обработка действия удаления
        habit_id = e.control.data
        self.model.delete_habit(habit_id)
        self.refresh_habit_list()

    def handle_show_dates(self, e):
        # Отображение таблички с датами
        habit_id = e.control.data
        habits = self.model.get_habits()
        for habit in habits:
            if habit[0] == habit_id:
                habit_name, frequency = habit[1], habit[3]
                today = datetime.now()
                if frequency == "Ежедневно":
                    start_date = today - timedelta(days=3)  # 3 дня назад
                    end_date = today + timedelta(days=3)  # 3 дня вперед
                else:  # Еженедельно
                    start_date = today - timedelta(weeks=3)  # 3 недели назад
                    end_date = today + timedelta(weeks=2)  # 2 недели вперед
                completions = self.model.get_completions(
                    habit_id,
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d")
                )
                self.view.create_date_dialog(habit_id, habit_name, frequency, completions, self.handle_date_change)
                break

    def handle_date_change(self, e, habit_id):
        # Обработка изменения состояния чекбокса
        date = e.control.data
        checked = e.control.value
        if checked:
            self.model.mark_completion(habit_id, date)
        else:
            self.model.unmark_completion(habit_id, date)
        # Обновление диалога
        habits = self.model.get_habits()
        for habit in habits:
            if habit[0] == habit_id:
                habit_name, frequency = habit[1], habit[3]
                today = datetime.now()
                if frequency == "Ежедневно":
                    start_date = today - timedelta(days=3)
                    end_date = today + timedelta(days=3)
                else:  # Еженедельно
                    start_date = today - timedelta(weeks=3)
                    end_date = today + timedelta(weeks=2)
                completions = self.model.get_completions(
                    habit_id,
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d")
                )
                self.view.create_date_dialog(habit_id, habit_name, frequency, completions, self.handle_date_change)
                break