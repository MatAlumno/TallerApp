import flet as ft
from db_connection import connect_to_db

class Herramienta_Repuesto:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None

        self.search_field = ft.TextField(label="Buscar", width=300, on_change=self.search)
        self.search_column = ft.Dropdown(
            options=[
                ft.dropdown.Option("id_repuesto"),
                ft.dropdown.Option("nombre"),
                ft.dropdown.Option("descripcion"),
            ],
            value="nombre",
            width=200,
            on_change=self.search,
        )
        self.mostrar_repuesto()

    # Pantalla principal
    def mostrar_repuesto(self):
        self.page.clean()
        alta_btn = ft.ElevatedButton("Alta", on_click=self.alta)
        consulta_btn = ft.ElevatedButton("Consulta", on_click=self.consulta)
        imprimir_btn = ft.ElevatedButton("Imprimir")
        volver_btn = ft.ElevatedButton("Volver", on_click=lambda e: self.main_menu_callback(self.page))
        self.page.add(ft.Row([alta_btn, consulta_btn, imprimir_btn, volver_btn], alignment=ft.MainAxisAlignment.CENTER))
        self.page.update()

    # Alta de repuesto
    def alta(self, e):
        self.page.clean()
        self.nombre = ft.TextField(label="Nombre")
        self.descripcion = ft.TextField(label="Descripción")
        self.precio = ft.TextField(label="Precio")
        self.stock = ft.TextField(label="Stock")
        self.id_proveedor = ft.TextField(label="ID Proveedor")

        guardar_btn = ft.ElevatedButton("Guardar", on_click=self.guardar)
        volver_btn = ft.ElevatedButton("Volver", on_click=lambda e: self.mostrar_repuesto())
        self.page.add(self.nombre, self.descripcion, self.precio, self.stock, self.id_proveedor,
                      ft.Row([guardar_btn, volver_btn]))
        self.page.update()

    def guardar(self, e):
        try:
            query = "INSERT INTO repuesto (nombre, descripcion, precio, stock, id_proveedor) VALUES (%s, %s, %s, %s, %s)"
            values = (self.nombre.value, self.descripcion.value, self.precio.value, self.stock.value, self.id_proveedor.value)
            self.cursor.execute(query, values)
            self.connection.commit()
            self.page.snack_bar = ft.SnackBar(ft.Text("Repuesto agregado exitosamente"))
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
                ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Stock")),
                ft.DataColumn(ft.Text("ID Proveedor")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]
        )
        volver_btn = ft.ElevatedButton("Volver", on_click=lambda e: self.mostrar_repuesto())
        self.page.add(ft.Row([self.search_field, self.search_column], alignment=ft.MainAxisAlignment.CENTER))
        self.page.add(self.data_table, volver_btn)
        self.cargar_datos()
        self.page.update()

    def cargar_datos(self, filtro_columna=None, filtro_valor=None):
        self.data_table.rows.clear()
        try:
            query = "SELECT id_repuesto, nombre, descripcion, precio, stock, id_proveedor FROM repuesto"
            if filtro_columna and filtro_valor:
                query += f" WHERE {filtro_columna} LIKE %s"
                self.cursor.execute(query, (f"%{filtro_valor}%",))
            else:
                self.cursor.execute(query)
            for fila in self.cursor.fetchall():
                self.data_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(fila[0]))),
                            ft.DataCell(ft.Text(fila[1])),
                            ft.DataCell(ft.Text(fila[2])),
                            ft.DataCell(ft.Text(str(fila[3]))),
                            ft.DataCell(ft.Text(str(fila[4]))),
                            ft.DataCell(ft.Text(str(fila[5]))),
                            ft.DataCell(ft.Row([
                                ft.IconButton(ft.icons.EDIT, on_click=lambda e, id=fila[0]: self.editar(id)),
                                ft.IconButton(ft.icons.DELETE, on_click=lambda e, id=fila[0]: self.eliminar(id)),
                            ]))
                        ]
                    )
                )
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error cargando datos: {ex}"))
            self.page.snack_bar.open = True
        self.page.update()

    def editar(self, id_repuesto):
        self.cursor.execute("SELECT nombre, descripcion, precio, stock, id_proveedor FROM repuesto WHERE id_repuesto = %s", (id_repuesto,))
        fila = self.cursor.fetchone()
        if not fila: return
        self.page.clean()
        self.nombre = ft.TextField(label="Nombre", value=fila[0])
        self.descripcion = ft.TextField(label="Descripción", value=fila[1])
        self.precio = ft.TextField(label="Precio", value=str(fila[2]))
        self.stock = ft.TextField(label="Stock", value=str(fila[3]))
        self.id_proveedor = ft.TextField(label="ID Proveedor", value=str(fila[4]))
        guardar_btn = ft.ElevatedButton("Actualizar", on_click=lambda e: self.actualizar(id_repuesto))
        volver_btn = ft.ElevatedButton("Volver", on_click=lambda e: self.consulta(None))
        self.page.add(self.nombre, self.descripcion, self.precio, self.stock, self.id_proveedor,
                      ft.Row([guardar_btn, volver_btn]))
        self.page.update()

    def actualizar(self, id_repuesto):
        try:
            query = "UPDATE repuesto SET nombre=%s, descripcion=%s, precio=%s, stock=%s, id_proveedor=%s WHERE id_repuesto=%s"
            values = (self.nombre.value, self.descripcion.value, self.precio.value, self.stock.value, self.id_proveedor.value, id_repuesto)
            self.cursor.execute(query, values)
            self.connection.commit()
            self.page.snack_bar = ft.SnackBar(ft.Text("Repuesto actualizado exitosamente"))
            self.page.snack_bar.open = True
            self.consulta(None)
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al actualizar: {ex}"))
            self.page.snack_bar.open = True
        self.page.update()

    def eliminar(self, id_repuesto):
        try:
            self.cursor.execute("DELETE FROM repuesto WHERE id_repuesto = %s", (id_repuesto,))
            self.connection.commit()
            self.page.snack_bar = ft.SnackBar(ft.Text("Repuesto eliminado"))
            self.page.snack_bar.open = True
            self.consulta(None)
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar: {ex}"))
            self.page.snack_bar.open = True
        self.page.update()

    def search(self, e):
        self.cargar_datos(self.search_column.value, self.search_field.value)
