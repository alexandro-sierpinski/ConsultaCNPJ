import flet as ft

class CNPJView(ft.UserControl):
    def __init__(self, presenter):
        super().__init__()
        self.presenter = presenter
        self.file_picker = ft.FilePicker(on_result=self.presenter.on_file_picked)
        self.loading_text = ft.Text("", color=ft.colors.BLUE, size=16, visible=False)

    def build(self):
        # Definindo os controles
        self.cnpj_input = ft.TextField(
            label="CNPJ",
            width=400,
            border_radius=10,
            text_align=ft.TextAlign.CENTER,
            hint_text="Digite o CNPJ",
            on_change=self.on_cnpj_change,
        )

        self.check_button = ft.ElevatedButton(
            text="Checar",
            on_click=self.presenter.on_check_clicked,
            width=200,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                bgcolor=ft.colors.BLUE_ACCENT,
            ),
        )

        self.file_button = ft.IconButton(
            icon=ft.icons.FOLDER_OPEN,
            icon_color=ft.colors.BLUE_GREY,
            on_click=self.open_file_picker,
        )

        # Adicionando o FilePicker e outros controles à página
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Consulta de CNPJ",
                        style=ft.TextStyle(
                            weight=ft.FontWeight.BOLD, size=24
                        ),
                        color=ft.colors.BLUE,
                    ),
                    ft.Container(height=30),  # Espaçamento entre o título e o campo de entrada
                    self.cnpj_input,
                    ft.Container(height=20),  # Espaçamento entre o campo de entrada e o botão
                    self.check_button,
                    ft.Container(height=20),  # Espaçamento entre os botões
                    ft.Text("Ou selecione um arquivo XLSX:", color=ft.colors.BLUE),
                    self.file_button,
                    # Adicionando o FilePicker ao layout
                    self.file_picker,
                    # Indicador de carregamento
                    self.loading_text
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
            padding=20,
            height=600,
        )

    def open_file_picker(self, e):
        # Certifique-se de que o FilePicker foi adicionado à página
        if self.file_picker:
            self.file_picker.pick_files()

    def on_cnpj_change(self, e):
        # Remove espaços e garante que apenas números sejam aceitos
        cnpj = e.control.value
        cleaned_cnpj = ''.join(filter(str.isdigit, cnpj))
        if cleaned_cnpj != cnpj:
            self.cnpj_input.value = cleaned_cnpj
            e.control.update()

    def show_loading(self, message):
        self.loading_text.value = message
        self.loading_text.visible = True
        self.update()

    def hide_loading(self):
        self.loading_text.visible = False
        self.update()