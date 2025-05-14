import flet as ft
from datetime import datetime, timedelta

class HabitTrackerView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Трекер привычек"
        self.habit_list = ft.ListView(expand=True, spacing=10, padding=20)
        self.add_form = self.create_add_form()
        self.dialog = None

    def create_add_form(self):
        # Создание формы для добавления/редактирования привычек
        name_field = ft.TextField(label="Название привычки", width=200)
        desc_field = ft.TextField(label="Описание", width=300)
        freq_dropdown = ft.Dropdown(
            label="Периодичность",
            options=[
                ft.dropdown.Option("Ежедневно"),
                ft.dropdown.Option("Еженедельно")
            ],
            width=150
        )
        save_button = ft.ElevatedButton("Сохранить", data=None)  # data будет содержать habit_id для редактирования
        cancel_button = ft.ElevatedButton("Отмена")
        return ft.Row([name_field, desc_field, freq_dropdown, save_button, cancel_button])

    def create_date_dialog(self, habit_id, habit_name, frequency, completions, on_date_change):
        # Создание диалогового окна с табличкой дат
        today = datetime.now()
        if frequency == "Ежедневно":
            start_date = today - timedelta(days=3)  # 3 дня назад
            end_date = today + timedelta(days=3)    # 3 дня вперед
            dates = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]  # Всего 7 дней
            title = "Отметить дни"
        else:  # Еженедельно
            start_date = today - timedelta(weeks=3)  # 3 недели назад
            end_date = today + timedelta(weeks=2)    # 2 недели вперед
            dates = [(start_date + timedelta(weeks=i)).strftime("%Y-%m-%d") for i in range(5)]  # Всего 5 недель
            title = "Отметить недели"

        checkboxes = []
        for date in dates:
            checked = date in completions
            checkbox = ft.Checkbox(
                label=f"{date} ({'Выполнено' if checked else 'Не выполнено'})",
                value=checked,
                data=date,
                on_change=lambda e, hid=habit_id: on_date_change(e, hid)
            )
            checkboxes.append(checkbox)

        self.dialog = ft.AlertDialog(
            title=ft.Text(f"{title}: {habit_name}"),
            content=ft.Column(checkboxes, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.ElevatedButton("Закрыть", on_click=lambda e: self.close_dialog())
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()

    def close_dialog(self):
        # Закрытие диалогового окна
        if self.dialog:
            self.dialog.open = False
            self.page.update()

    def update_habit_list(self, habits, on_mark, on_edit, on_delete, on_show_dates):
        # Обновление списка привычек
        self.habit_list.controls.clear()
        for habit in habits:
            habit_id, name, description, frequency = habit
            mark_button = ft.ElevatedButton("Отметить выполнение", data=habit_id, on_click=on_mark)
            dates_button = ft.ElevatedButton("Отметить даты", data=habit_id, on_click=on_show_dates)
            edit_button = ft.ElevatedButton("Редактировать", data=habit_id, on_click=on_edit)
            delete_button = ft.ElevatedButton("Удалить", data=habit_id, on_click=on_delete)
            self.habit_list.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"{name} ({'Ежедневно' if frequency == 'Ежедневно' else 'Еженедельно'})"),
                                ft.Text(f"Описание: {description}")
                            ]),
                            ft.Row([
                                mark_button,
                                dates_button,
                                edit_button,
                                delete_button
                            ])
                        ]),
                        padding=10
                    )
                )
            )
        self.page.update()

    def populate_edit_form(self, habit_id, name, description, frequency):
        # Заполнение формы для редактирования привычки
        self.add_form.controls[0].value = name
        self.add_form.controls[1].value = description
        self.add_form.controls[2].value = frequency
        self.add_form.controls[3].data = habit_id
        self.page.update()

    def clear_form(self):
        # Очистка формы добавления/редактирования
        self.add_form.controls[0].value = ""
        self.add_form.controls[1].value = ""
        self.add_form.controls[2].value = ""
        self.add_form.controls[3].data = None
        self.page.update()

    def setup_page(self, on_save, on_cancel):
        # Настройка основного макета страницы
        self.add_form.controls[3].on_click = on_save  # Кнопка Сохранить
        self.add_form.controls[4].on_click = on_cancel  # Кнопка Отмена
        self.page.add(self.add_form, self.habit_list)