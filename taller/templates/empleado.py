import flet as ft
from db_connection import connect_to_db

class Herramienta_Empleado:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None
        self.search_field = ft.TextField(label="Buscar", width=300, on_change=self.search)
        self.search_column = ft.Dropdown(
            options=[
                ft.dropdown.Option("cod_empleado"),
                ft.dropdown.Option("nombre"),
                ft.dropdown.Option("apellido"),
                ft.dropdown.Option("cargo"),
            ],
            value="cod_empleado",
            width=200,
            on_change=self.search,
        )
        self.mostrar_empleado()

    # Pantalla principal
    def mostrar_empleado(self):
        self.page.clean()
        alta_btn = ft.ElevatedButton("Alta", on_click=self.alta)
        consulta_btn = ft.ElevatedButton("Consulta", on_click=self.consulta)
        imprimir_btn = ft.ElevatedButton("Imprimir")
        volver_btn = ft.ElevatedButton("Volver", on_click=lambda e: self.main_menu_callback(self.page))
        self.page.add(ft.Row([alta_btn, consulta_btn, imprimir_btn, volver_btn], alignment=ft.MainAxisAlignment.CENTER))
        self.page.update()

    # Alta de empleado
    def alta(self, e):
        self.page.clean()
        self.nombre = ft.TextField(label="Nombre")
        self.apellido = ft.TextField(label="Apellido")
        self.cargo = ft.TextField(label="Cargo")
        guardar_btn = ft.ElevatedButton("Guardar", on_click=self.guardar)
        volver_btn = ft.ElevatedButton("Volver", on_click=lambda e: self.mostrar_empleado())
        self.page.add(self.nombre, self.apellido, self.cargo, ft.Row([guardar_btn, volver_btn]))
        self.page.update()

    def guardar(self, e):
        try:
            query = "INSERT INTO empleado (nombre, apellido, cargo) VALUES (%s, %s, %s)"
            values = (self.nombre.value, self.apellido.value, self.cargo.value)
            self.cursor.execute(query, values)
            self.connection.commit()
            self.page.snack_bar = ft.SnackBar(ft.Text("Empleado agregado exitosamente"))
            self.page.snack_bar.open = True
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"))
            self.page.snack_bar.open = True
        self.page.update()

    # Consulta
    def consulta(self, e):
        self.page.clean()
        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Apellido")),
                ft.DataColumn(ft.Text("Cargo")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]
        )
        volver_btn = ft.ElevatedButton("Volver", on_click=lambda e: self.mostrar_empleado())
        self.page.add(ft.Row([self.search_field, self.search_column], alignment=ft.MainAxisAlignment.CENTER))
        self.page.add(self.data_table, volver_btn)
        self.cargar_datos()
        self.page.update()

    def cargar_datos(self, filtro_columna=None, filtro_valor=None):
        self.data_table.rows.clear()
        query = "SELECT * FROM empleado"
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
        self.cursor.execute("SELECT * FROM empleado WHERE cod_empleado = %s", (id,))
        empleado = self.cursor.fetchone()
        self.nombre = ft.TextField(label="Nombre", value=empleado[1])
        self.apellido = ft.TextField(label="Apellido", value=empleado[2])
        self.cargo = ft.TextField(label="Cargo", value=empleado[3])
        guardar_btn = ft.ElevatedButton("Guardar cambios", on_click=lambda e: self.actualizar(id))
        volver_btn = ft.ElevatedButton("Volver", on_click=lambda e: self.consulta(None))
        self.page.add(self.nombre, self.apellido, self.cargo, ft.Row([guardar_btn, volver_btn]))
        self.page.update()

    def actualizar(self, id):
        query = "UPDATE empleado SET nombre=%s, apellido=%s, cargo=%s WHERE cod_empleado=%s"
        values = (self.nombre.value, self.apellido.value, self.cargo.value, id)
        self.cursor.execute(query, values)
        self.connection.commit()
        self.page.snack_bar = ft.SnackBar(ft.Text("Empleado actualizado exitosamente"))
        self.page.snack_bar.open = True
        self.consulta(None)

    def eliminar(self, id):
        query = "DELETE FROM empleado WHERE cod_empleado=%s"
        self.cursor.execute(query, (id,))
        self.connection.commit()
        self.page.snack_bar = ft.SnackBar(ft.Text("Empleado eliminado"))
        self.page.snack_bar.open = True
        self.consulta(None)

    def search(self, e):
        self.cargar_datos(self.search_column.value, self.search_field.value)
