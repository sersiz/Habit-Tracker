import flet as ft
from views import HabitTrackerView
from controllers import HabitTrackerController
from models import HabitModel


def main(page: ft.Page):
    # Инициализация компонентов MVC
    page.title = "Трекер привычек"
    model = HabitModel()
    view = HabitTrackerView(page)
    controller = HabitTrackerController(model, view)

    # Настройка начального вида
    controller.setup_view()


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)