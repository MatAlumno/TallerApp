import flet as ft
from db_connection import connect_to_db

class Herramienta_Cliente:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None
        self.search_field = ft.TextField(label="Buscar", width=300, on_change=self.search)
        self.search_column = ft.Dropdown(
            options=[
                ft.dropdown.Option("cod_cliente"),
                ft.dropdown.Option("nombre"),
                ft.dropdown.Option("apellido"),
                ft.dropdown.Option("dni"),
                ft.dropdown.Option("telefono"),
            ],
            value="cod_cliente",
            width=200,
            on_change=self.search,
        )
        self.mostrar_cliente()

    # Pantalla principal
    def mostrar_cliente(self):
        self.page.clean()
        alta_btn = ft.ElevatedButton("Alta", on_click=self.alta)
        consulta_btn = ft.ElevatedButton("Consulta", on_click=self.consulta)
        imprimir_btn = ft.ElevatedButton("Imprimir")
        volver_btn = ft.ElevatedButton("Volver", on_click=lambda e: self.main_menu_callback(self.page))
        self.page.add(ft.Row([alta_btn, consulta_btn, imprimir_btn, volver_btn], alignment=ft.MainAxisAlignment.CENTER))
        self.page.update()

    # Alta de cliente
    def alta(self, e):
        self.page.clean()
        self.nombre = ft.TextField(label="Nombre")
        self.apellido = ft.TextField(label="Apellido")
        self.dni = ft.TextField(label="DNI")
        self.telefono = ft.TextField(label="Teléfono")
        guardar_btn = ft.ElevatedButton("Guardar", on_click=self.guardar)
        volver_btn = ft.ElevatedButton("Volver", on_click=lambda e: self.mostrar_cliente())
        self.page.add(self.nombre, self.apellido, self.dni, self.telefono, ft.Row([guardar_btn, volver_btn]))
        self.page.update()

    def guardar(self, e):
        try:
            query = "INSERT INTO cliente (nombre, apellido, dni, telefono) VALUES (%s, %s, %s, %s)"
            values = (self.nombre.value, self.apellido.value, self.dni.value, self.telefono.value)
            self.cursor.execute(query, values)
            self.connection.commit()
            self.page.snack_bar = ft.SnackBar(ft.Text("Cliente agregado exitosamente"))
            self.page.snack_bar.open = True
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"))
            self.page.snack_bar.open = True
        self.page.update()

    # Consulta de clientes
    def consulta(self, e):
        self.page.clean()
        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Apellido")),
                ft.DataColumn(ft.Text("DNI")),
                ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]
        )
        volver_btn = ft.ElevatedButton("Volver", on_click=lambda e: self.mostrar_cliente())
        self.page.add(ft.Row([self.search_field, self.search_column], alignment=ft.MainAxisAlignment.CENTER))
        self.page.add(self.data_table, volver_btn)
        self.cargar_datos()
        self.page.update()

    def cargar_datos(self, filtro_columna=None, filtro_valor=None):
        self.data_table.rows.clear()
        query = "SELECT * FROM cliente"
        values = None
        if filtro_columna and filtro_valor:
            query += f" WHERE {filtro_columna} LIKE %s"
            values = (f"%{filtro_valor}%",)
        self.cursor.execute(query, values) if values else self.cursor.execute(query)
        for row in self.cursor.fetchall():
            self.data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row[0]))),
                        ft.DataCell(ft.Text(row[1])),
                        ft.DataCell(ft.Text(row[2])),
                        ft.DataCell(ft.Text(row[3])),
                        ft.DataCell(ft.Text(row[4])),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(ft.Icons.EDIT, on_click=lambda e, id=row[0]: self.editar(id)),
                                    ft.IconButton(ft.Icons.DELETE, on_click=lambda e, id=row[0]: self.eliminar(id)),
                                ]
                            )
                        ),
                    ]
                )
            )
        self.page.update()

    def editar(self, id):
        self.page.clean()
        self.cursor.execute("SELECT * FROM cliente WHERE cod_cliente = %s", (id,))
        cliente = self.cursor.fetchone()
        self.nombre = ft.TextField(label="Nombre", value=cliente[1])
        self.apellido = ft.TextField(label="Apellido", value=cliente[2])
        self.dni = ft.TextField(label="DNI", value=cliente[3])
        self.telefono = ft.TextField(label="Teléfono", value=cliente[4])
        guardar_btn = ft.ElevatedButton("Guardar cambios", on_click=lambda e: self.actualizar(id))
        volver_btn = ft.ElevatedButton("Volver", on_click=lambda e: self.consulta(None))
        self.page.add(self.nombre, self.apellido, self.dni, self.telefono, ft.Row([guardar_btn, volver_btn]))
        self.page.update()

    def actualizar(self, id):
        query = "UPDATE cliente SET nombre=%s, apellido=%s, dni=%s, telefono=%s WHERE cod_cliente=%s"
        values = (self.nombre.value, self.apellido.value, self.dni.value, self.telefono.value, id)
        self.cursor.execute(query, values)
        self.connection.commit()
        self.page.snack_bar = ft.SnackBar(ft.Text("Cliente actualizado exitosamente"))
        self.page.snack_bar.open = True
        self.consulta(None)

    def eliminar(self, id):
        query = "DELETE FROM cliente WHERE cod_cliente=%s"
        self.cursor.execute(query, (id,))
        self.connection.commit()
        self.page.snack_bar = ft.SnackBar(ft.Text("Cliente eliminado"))
        self.page.snack_bar.open = True
        self.consulta(None)

    def search(self, e):
        self.cargar_datos(self.search_column.value, self.search_field.value)
