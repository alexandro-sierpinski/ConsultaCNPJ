import flet as ft
from view import CNPJView
from presenter import CNPJPresenter

def main(page: ft.Page):
    presenter = CNPJPresenter(None)
    view = CNPJView(presenter)
    presenter.view = view  # Para evitar problemas de dependência circular
    page.add(view)

ft.app(target=main)