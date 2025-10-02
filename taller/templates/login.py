import flet as ft
from db_connection import connect_to_db

def create_login_view(page: ft.Page, on_login_success):

    username = ft.TextField(label="Usuario")
    password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True)

    def login(e):
        try:
            connection = connect_to_db()
            if connection and connection.is_connected():
                cursor = connection.cursor()
                query = "SELECT * FROM usuarios WHERE username = %s AND password = %s"
                cursor.execute(query, (username.value, password.value))
                result = cursor.fetchone()

                if result:
                    on_login_success()
                else:
                    page.add(ft.Text("Credenciales incorrectas", color=ft.Colors.RED))
            else:
                page.add(ft.Text("Error de conexión a la base de datos", color=ft.Colors.RED))
        except Exception as ex:
            page.add(ft.Text(f"Error: {ex}", color=ft.Colors.RED))
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
        page.update()

    return ft.View(
        "/login",
        [
            ft.AppBar(title=ft.Text("Login")),
            username,
            password,
            ft.ElevatedButton("Login", on_click=login),
        ],
    )
