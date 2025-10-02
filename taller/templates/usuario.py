import flet as ft
from db_connection import connect_to_db

class Herramienta_Usuario:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.mostrar_login()

    def mostrar_login(self):
        self.page.clean()
        self.usuario = ft.TextField(label="Usuario", width=300)
        self.contrasena = ft.TextField(label="Contraseña", password=True, width=300)
        iniciar_btn = ft.ElevatedButton("Iniciar sesión", on_click=self.login)
        volver_btn = ft.ElevatedButton("Volver", icon=ft.Icons.ARROW_BACK, on_click=lambda e: self.main_menu_callback(self.page))

        self.page.add(
            ft.Column(
                [
                    ft.Text("Inicio de Sesión", size=24, weight="bold"),
                    self.usuario,
                    self.contrasena,
                    ft.Row([iniciar_btn, volver_btn], spacing=10),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        self.page.update()

    def login(self, e):
        try:
            connection = connect_to_db()
            if connection and connection.is_connected():
                cursor = connection.cursor()
                query = "SELECT * FROM usuarios WHERE username = %s AND password = %s"
                cursor.execute(query, (self.usuario.value, self.contrasena.value))
                result = cursor.fetchone()

                if result:
                    self.page.snack_bar = ft.SnackBar(ft.Text("Inicio de sesión exitoso"))
                    self.page.snack_bar.open = True
                    self.page.clean()
                    self.main_menu_callback(self.page)
                else:
                    self.page.snack_bar = ft.SnackBar(ft.Text("Credenciales incorrectas"))
                    self.page.snack_bar.open = True
            else:
                self.page.snack_bar = ft.SnackBar(ft.Text("Error de conexión a la base de datos"))
                self.page.snack_bar.open = True
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"))
            self.page.snack_bar.open = True
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
        self.page.update()
