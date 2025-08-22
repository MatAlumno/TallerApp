'''import flet as ft
from db import connect_to_db

def usuario_page(page: ft.Page):
    container = ft.View()
    dt = ft.DataTable(
        columns=[ft.DataColumn(ft.Text("ID Usuario")), ft.DataColumn(ft.Text("Nombre")), ft.DataColumn(ft.Text("Rol"))],
        rows=[]
    )

    def load_data():
        dt.rows.clear()
        db = connect_to_db()
        cursor = db.cursor()
        cursor.execute("SELECT id_usuario, nombre, rol FROM usuario")
        for idu, nombre, rol in cursor.fetchall():
            dt.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(idu)), ft.DataCell(ft.Text(nombre)), ft.DataCell(ft.Text(rol))]))
        db.close()
        page.update()

    def add_usuario(e):
        db = connect_to_db()
        cursor = db.cursor()
        idu = ft.time.time_ns()%10000
        cursor.execute("INSERT INTO usuario (id_usuario, nombre, rol) VALUES (%s,%s,%s)", (idu,"Usuario X","admin"))
        db.commit()
        db.close()
        load_data()

    container.controls.extend([
        dt,
        ft.Row([ft.ElevatedButton("Agregar", on_click=add_usuario),
                ft.ElevatedButton("Volver", on_click=lambda e: page.views.pop())])
    ])
    load_data()
    return container

//////////

import flet as ft
import mysql.connector

def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='1234',
            database='Taller_Mecanico'
        )
        if connection.is_connected():
            print('Conexión exitosa')
            return connection
    except Exception as ex:
        print('Conexión errónea')
        print(ex)
        return None

class Herramienta_Usuario:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None
        self.mostrar_usuario()

    def mostrar_usuario(self):
        self.page.clean()
        header = ft.Row(
            controls=[
                ft.Text("Herramienta de Gestión de Usuarios", size=20, weight="bold"),
                ft.ElevatedButton(text="Alta"),
                ft.ElevatedButton(text="Consulta"),
                ft.ElevatedButton(text="Imprimir"),
                ft.ElevatedButton(text="<--Volver al Menú", on_click=self.volver_al_menu),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
        data_table = self.create_user_table()
        self.page.add(
            ft.Container(
                content=ft.Column(
                    controls=[
                        header,
                        data_table
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20
            )
        )

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback(self.page)

    def create_user_table(self):
        if not self.cursor:
            print("No hay conexión a la base de datos")
            return ft.Text("No hay conexión a la base de datos")

        consulta_usuarios = """
            SELECT u.id_usuario, u.username, u.rol, u.estado
            FROM usuario u
            ORDER BY u.username
        """
        self.cursor.execute(consulta_usuarios)
        datos_usuarios = self.cursor.fetchall()
        rows = []

        for usuario in datos_usuarios:
            eliminar_button = ft.Container(
                content=ft.Image(src="assets/bote-de-basura.png", width=28, height=28, tooltip="Borrar"),
                on_click=lambda e, u=usuario: self.eliminar_usuario(e, u),
                ink=True,
                padding=5
            )

            actualizar_button = ft.Container(
                content=ft.Image(src="assets/modificar.png", width=28, height=28, tooltip="Modificar"),
                on_click=lambda e, u=usuario: self.actualizar_usuario(e, u),
                ink=True,
                padding=5
            )

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(usuario[0]))),
                        ft.DataCell(ft.Text(usuario[1])),
                        ft.DataCell(ft.Text(usuario[2])),
                        ft.DataCell(ft.Text(usuario[3])),
                        ft.DataCell(
                            ft.Row(
                                controls=[
                                    eliminar_button,
                                    actualizar_button
                                ]
                            )
                        )
                    ],
                ),
            )

        data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID Usuario")),
                ft.DataColumn(ft.Text("Username")),
                ft.DataColumn(ft.Text("Rol")),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=rows,
        )
        return data_table

    def eliminar_usuario(self, e, usuario):
        print(f"Eliminar usuario {usuario[1]}")

    def actualizar_usuario(self, e, usuario):
        print(f"Actualizar usuario {usuario[1]}")

import flet as ft
from db import connect_to_db

def usuario_page(page: ft.Page):
    container = ft.View()
    dt = ft.DataTable(
        columns=[ft.DataColumn(ft.Text("ID Usuario")), ft.DataColumn(ft.Text("Nombre")), ft.DataColumn(ft.Text("Rol"))],
        rows=[]
    )

    def load_data():
        dt.rows.clear()
        db = connect_to_db()
        cursor = db.cursor()
        cursor.execute("SELECT id_usuario, nombre, rol FROM usuario")
        for idu, nombre, rol in cursor.fetchall():
            dt.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(idu)), ft.DataCell(ft.Text(nombre)), ft.DataCell(ft.Text(rol))]))
        db.close()
        page.update()

    def add_usuario(e):
        db = connect_to_db()
        cursor = db.cursor()
        idu = ft.time.time_ns()%10000
        cursor.execute("INSERT INTO usuario (id_usuario, nombre, rol) VALUES (%s,%s,%s)", (idu,"Usuario X","admin"))
        db.commit()
        db.close()
        load_data()

    container.controls.extend([
        dt,
        ft.Row([ft.ElevatedButton("Agregar", on_click=add_usuario),
                ft.ElevatedButton("Volver", on_click=lambda e: page.views.pop())])
    ])
    load_data()
    return container
'''