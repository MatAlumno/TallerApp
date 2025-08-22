import flet as ft
from db import connect_to_db

class Pagina_Cliente:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None

        self.search_field = ft.TextField(label="Buscar", width=300, on_change=self.search)
        self.search_column = ft.Dropdown(
            options=[
                ft.dropdown.Option("id_cliente", text="ID Cliente"),
                ft.dropdown.Option("dni", text="DNI"),
                ft.dropdown.Option("fecha_registro", text="Fecha de Registro"),
            ],
            value="id_cliente",
            width=200,
            on_change=self.search,
        )

        self.all_data = []
        self.data_table = None
        self.mostrar_cliente()

    def mostrar_cliente(self):
        self.page.clean()

        header = ft.Row(
            controls=[
                ft.Text("Gestión de Clientes", size=20, weight="bold"),
                ft.ElevatedButton("Alta", on_click=self.alta_cliente),
                ft.ElevatedButton("Consulta", on_click=self.consulta_cliente),
                ft.ElevatedButton("Imprimir", on_click=self.imprimir_clientes),
                ft.ElevatedButton("Volver al Menú", on_click=self.volver_al_menu),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        search_row = ft.Row(
            controls=[self.search_column, self.search_field],
            alignment=ft.MainAxisAlignment.START,
        )

        self.data_table = self.create_client_table()

        self.page.add(
            ft.Container(
                content=ft.Column(
                    controls=[header, search_row, self.data_table],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                ),
                padding=20
            )
        )

    def alta_cliente(self, e):
        self.page.clean()
        self.dni = ft.TextField(label="DNI", width=300)
        self.nombre = ft.TextField(label="Nombre", width=300)
        self.apellido = ft.TextField(label="Apellido", width=300)
        self.fecha_registro = ft.TextField(label="Fecha de Registro YYYY-MM-DD", width=300)

        guardar_btn = ft.ElevatedButton("Guardar", on_click=self.guardar_cliente)
        volver_btn = ft.ElevatedButton("Volver", on_click=self.volver_al_menu)

        self.page.add(
            ft.Column(
                controls=[
                    ft.Text("Alta de Cliente", size=24, weight="bold"),
                    self.dni,
                    self.nombre,
                    self.apellido,
                    self.fecha_registro,
                    ft.Row([guardar_btn, volver_btn], spacing=10)
                ],
                spacing=10
            )
        )
        self.page.update()

    def guardar_cliente(self, e):
        if not self.cursor:
            return
        try:
            self.cursor.execute(
                "INSERT INTO persona (dni, nombre, apellido) VALUES (%s, %s, %s)",
                (self.dni.value, self.nombre.value, self.apellido.value)
            )
            self.cursor.execute(
                "INSERT INTO cliente (dni, fecha_registro) VALUES (%s, %s)",
                (self.dni.value, self.fecha_registro.value)
            )
            self.connection.commit()
            print("Cliente guardado correctamente")
            self.page.snack_bar = ft.SnackBar(ft.Text("Cliente guardado correctamente"))
            self.page.snack_bar.open = True
            self.mostrar_cliente()
        except Exception as ex:
            print(f"Error al guardar: {ex}")
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al guardar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def consulta_cliente(self, e):
        self.mostrar_cliente()

    def imprimir_clientes(self, e):
        print("Función de impresión no implementada")
        self.page.snack_bar = ft.SnackBar(ft.Text("Función de impresión no implementada"))
        self.page.snack_bar.open = True
        self.page.update()

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback(self.page)

    def create_client_table(self):
        if not self.cursor:
            return ft.Text("No hay conexión a la base de datos")
        try:
            self.cursor.execute("""
                SELECT c.id_cliente, c.dni, p.nombre, p.apellido, c.fecha_registro
                FROM cliente c
                JOIN persona p ON c.dni = p.dni
                ORDER BY c.id_cliente
            """)
            datos = self.cursor.fetchall()
            self.all_data = datos
            return ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID Cliente")),
                    ft.DataColumn(ft.Text("DNI")),
                    ft.DataColumn(ft.Text("Nombre")),
                    ft.DataColumn(ft.Text("Apellido")),
                    ft.DataColumn(ft.Text("Fecha Registro")),
                    ft.DataColumn(ft.Text("Acciones")),
                ],
                rows=self.get_rows(datos)
            )
        except Exception as ex:
            return ft.Text(f"Error al cargar clientes: {ex}")

    def get_rows(self, clientes):
        rows = []
        for c in clientes:
            eliminar_btn = ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar", on_click=lambda e, cliente=c: self.eliminar_cliente(e, cliente))
            actualizar_btn = ft.IconButton(icon=ft.Icons.EDIT, tooltip="Actualizar", on_click=lambda e, cliente=c: self.actualizar_cliente(e, cliente))
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(c[0]))),
                        ft.DataCell(ft.Text(c[1])),
                        ft.DataCell(ft.Text(c[2])),
                        ft.DataCell(ft.Text(c[3])),
                        ft.DataCell(ft.Text(str(c[4]))),
                        ft.DataCell(ft.Row([eliminar_btn, actualizar_btn])),
                    ]
                )
            )
        return rows

    def search(self, e):
        term = self.search_field.value.lower()
        column = self.search_column.value
        filtered = []
        for row in self.all_data:
            if column == "id_cliente" and str(row[0]).lower().__contains__(term):
                filtered.append(row)
            elif column == "dni" and str(row[1]).lower().__contains__(term):
                filtered.append(row)
            elif column == "fecha_registro" and str(row[4]).lower().__contains__(term):
                filtered.append(row)
        self.data_table.rows = self.get_rows(filtered)
        self.page.update()

    def eliminar_cliente(self, e, cliente):
        if not self.cursor:
            return
        try:
            self.cursor.execute("DELETE FROM cliente WHERE id_cliente=%s", (cliente[0],))
            self.connection.commit()
            print("Cliente eliminado correctamente")
            self.page.snack_bar = ft.SnackBar(ft.Text("Cliente eliminado correctamente"))
            self.page.snack_bar.open = True
            self.mostrar_cliente()
        except Exception as ex:
            print(f"Error al eliminar: {ex}")
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def actualizar_cliente(self, e, cliente):
        self.page.clean()
        self.dni = ft.TextField(label="DNI", value=cliente[1], width=300)
        self.nombre = ft.TextField(label="Nombre", value=cliente[2], width=300)
        self.apellido = ft.TextField(label="Apellido", value=cliente[3], width=300)
        self.fecha_registro = ft.TextField(label="Fecha de Registro", value=str(cliente[4]), width=300)

        guardar_btn = ft.ElevatedButton("Guardar Cambios", on_click=lambda e: self.guardar_cambios_cliente(e, cliente))
        volver_btn = ft.ElevatedButton("Volver", on_click=self.volver_al_menu)

        self.page.add(
            ft.Column(
                controls=[
                    ft.Text("Actualizar Cliente", size=24, weight="bold"),
                    self.dni,
                    self.nombre,
                    self.apellido,
                    self.fecha_registro,
                    ft.Row([guardar_btn, volver_btn], spacing=10)
                ],
                spacing=10
            )
        )
        self.page.update()

    def guardar_cambios_cliente(self, e, cliente):
        if not self.cursor:
            return
        try:
            self.cursor.execute(
                "UPDATE persona SET nombre=%s, apellido=%s WHERE dni=%s",
                (self.nombre.value, self.apellido.value, self.dni.value)
            )
            self.cursor.execute(
                "UPDATE cliente SET fecha_registro=%s WHERE id_cliente=%s",
                (self.fecha_registro.value, cliente[0])
            )
            self.connection.commit()
            print("Cliente actualizado correctamente")
            self.page.snack_bar = ft.SnackBar(ft.Text("Cliente actualizado correctamente"))
            self.page.snack_bar.open = True
            self.mostrar_cliente()
        except Exception as ex:
            print(f"Error al actualizar: {ex}")
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al actualizar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()


'''

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

class Herramienta_Cliente:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None
        self.mostrar_cliente()

    def mostrar_cliente(self):
        self.bgcolor = ft.Colors.BLUE_50
        self.page.clean()
        header = ft.Row(
            controls=[
                ft.Text("Herramienta de Gestión de Clientes", size=20, weight="bold"),
                ft.ElevatedButton(text="Alta"),
                ft.ElevatedButton(text="Consulta"),
                ft.ElevatedButton(text="Imprimir"),
                ft.ElevatedButton(text="<--Volver al Menú", on_click=self.volver_al_menu),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
        data_table = self.create_client_table()
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

    def create_client_table(self):
        if not self.cursor:
            print("No hay conexión a la base de datos")
            return ft.Text("No hay conexión a la base de datos")

        listado_todos_clientes = """
            SELECT per.apellido, per.nombre, per.dni,
                   per.direccion, per.tele_contac, c.cod_cliente
            FROM persona per INNER JOIN cliente c ON per.dni = c.dni
            ORDER BY per.apellido
        """
        self.cursor.execute(listado_todos_clientes)
        datos_clientes = self.cursor.fetchall()
        rows = []

        for cliente in datos_clientes:
            eliminar_button = ft.Container(
                content=ft.Image(src="assets/bote-de-basura.png", width=28, height=28, tooltip="Borrar"),
                on_click=lambda e, c=cliente: self.eliminar_cliente(e, c),
                ink=True,
                padding=5
            )

            actualizar_button = ft.Container(
                content=ft.Image(src="assets/modificar.png", width=28, height=28,tooltip="Modificar"),
                on_click=lambda e, c=cliente: self.actualizar_cliente(e, c),
                ink=True,
                padding=5
            )

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(cliente[0])),
                        ft.DataCell(ft.Text(cliente[1])),
                        ft.DataCell(ft.Text(str(cliente[2]))),
                        ft.DataCell(ft.Text(cliente[3])),
                        ft.DataCell(ft.Text(cliente[4])),
                        ft.DataCell(ft.Text(str(cliente[5]))),
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
                ft.DataColumn(ft.Text("Apellido")),
                ft.DataColumn(ft.Text("Nombres")),
                ft.DataColumn(ft.Text("DNI")),
                ft.DataColumn(ft.Text("Direccion")),
                ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("Código de Cliente")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=rows,
        )
        return data_table

    def eliminar_cliente(self, e, cliente):
        print(f"Eliminar {cliente[0]}")

    def actualizar_cliente(self, e, cliente):
        print(f"Actualizar {cliente[0]}")

def main_menu_callback(page: ft.Page):
    page.clean()
    page.add(ft.Text("Menú Principal"))

def main(page: ft.Page):
    app = Herramienta_Cliente(page, main_menu_callback)

#ft.app(target=main)
'''