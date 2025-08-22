import flet as ft
from db import connect_to_db  

class Pagina_Repuesto:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None
        self.search_field = ft.TextField(label="Buscar", width=300, on_change=self.search)
        self.search_column = ft.Dropdown(
            options=[
                ft.dropdown.Option("nombre", text="Nombre"),
                ft.dropdown.Option("descripcion", text="Descripción"),
                ft.dropdown.Option("precio", text="Precio"),
                ft.dropdown.Option("stock", text="Stock"),
            ],
            value="nombre",
            width=200,
            on_change=self.search,
        )
        self.all_data = []
        self.mostrar_repuesto()

    def mostrar_repuesto(self):
        self.page.clean()
        header = ft.Row(
            controls=[
                ft.Text("Gestión de Repuestos", size=20, weight="bold"),
                ft.ElevatedButton("Alta", on_click=self.alta_repuesto),
                ft.ElevatedButton("Consulta", on_click=self.consulta_repuesto),
                ft.ElevatedButton("Imprimir", on_click=self.imprimir_repuestos),
                ft.ElevatedButton("Volver al Menú", on_click=self.volver_al_menu),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        search_row = ft.Row([self.search_column, self.search_field], alignment=ft.MainAxisAlignment.START)
        self.data_table = self.create_repuesto_table()
        self.page.add(
            ft.Container(
                content=ft.Column([header, search_row, self.data_table], spacing=10),
                padding=20
            )
        )

    def alta_repuesto(self, e):
        self.page.clean()
        self.nombre = ft.TextField(label="Nombre", width=300)
        self.descripcion = ft.TextField(label="Descripción", width=300)
        self.precio = ft.TextField(label="Precio", width=300)
        self.stock = ft.TextField(label="Stock", width=300)
        self.id_proveedor = ft.TextField(label="ID Proveedor", width=300)

        guardar_btn = ft.ElevatedButton("Guardar", on_click=self.guardar_repuesto)
        volver_btn = ft.ElevatedButton("Volver", on_click=self.volver_al_menu)

        self.page.add(ft.Column([
            ft.Text("Alta de Repuesto", size=24, weight="bold"),
            self.nombre, self.descripcion, self.precio, self.stock, self.id_proveedor,
            ft.Row([guardar_btn, volver_btn], spacing=10)
        ], spacing=10))

    def guardar_repuesto(self, e):
        if not self.cursor:
            return
        try:
            self.cursor.execute(
                "INSERT INTO repuesto (nombre, descripcion, precio, stock, id_proveedor) VALUES (%s, %s, %s, %s, %s)",
                (self.nombre.value, self.descripcion.value, self.precio.value, self.stock.value, self.id_proveedor.value)
            )
            self.connection.commit()
            print("Repuesto guardado correctamente")
            self.page.snack_bar = ft.SnackBar(ft.Text("Repuesto guardado correctamente"))
            self.page.snack_bar.open = True
            self.mostrar_repuesto()
        except Exception as ex:
            print(f"Error al guardar: {ex}")
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al guardar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def create_repuesto_table(self):
        if not self.cursor:
            return ft.Text("No hay conexión a la base de datos")
        self.cursor.execute("SELECT id_repuesto, nombre, descripcion, precio, stock, id_proveedor FROM repuesto ORDER BY id_repuesto")
        self.all_data = self.cursor.fetchall()
        rows = self.get_rows(self.all_data)
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID Repuesto")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Stock")),
                ft.DataColumn(ft.Text("ID Proveedor")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=rows
        )

    def get_rows(self, repuestos):
        rows = []
        for r in repuestos:
            eliminar_btn = ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar", on_click=lambda e, x=r: self.eliminar_repuesto(e, x))
            actualizar_btn = ft.IconButton(icon=ft.Icons.EDIT, tooltip="Modificar", on_click=lambda e, x=r: self.actualizar_repuesto(e, x))
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(r[0]))),  # id_repuesto
                ft.DataCell(ft.Text(r[1])),       # nombre
                ft.DataCell(ft.Text(r[2])),       # descripcion
                ft.DataCell(ft.Text(str(r[3]))),  # precio
                ft.DataCell(ft.Text(str(r[4]))),  # stock
                ft.DataCell(ft.Text(str(r[5]))),  # id_proveedor
                ft.DataCell(ft.Row([eliminar_btn, actualizar_btn]))
            ]))
        return rows

    def search(self, e):
        term = self.search_field.value.lower()
        col_index = self.get_column_index(self.search_column.value)
        filtered = [r for r in self.all_data if term in str(r[col_index]).lower()]
        self.data_table.rows = self.get_rows(filtered)
        self.page.update()

    def get_column_index(self, column_name):
        mapping = {"nombre": 1, "descripcion": 2, "precio": 3, "stock": 4}
        return mapping.get(column_name, 1)

    def eliminar_repuesto(self, e, r):
        try:
            self.cursor.execute("DELETE FROM repuesto WHERE id_repuesto=%s", (r[0],))
            self.connection.commit()
            print("Repuesto eliminado correctamente")
            self.page.snack_bar = ft.SnackBar(ft.Text("Repuesto eliminado correctamente"))
            self.page.snack_bar.open = True
            self.mostrar_repuesto()
        except Exception as ex:
            print(f"Error al eliminar: {ex}")
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def actualizar_repuesto(self, e, r):
        self.page.clean()
        self.id_repuesto = ft.TextField(label="ID Repuesto", value=str(r[0]), width=300, disabled=True)
        self.nombre = ft.TextField(label="Nombre", value=r[1], width=300)
        self.descripcion = ft.TextField(label="Descripción", value=r[2], width=300)
        self.precio = ft.TextField(label="Precio", value=str(r[3]), width=300)
        self.stock = ft.TextField(label="Stock", value=str(r[4]), width=300)
        self.id_proveedor = ft.TextField(label="ID Proveedor", value=str(r[5]), width=300)

        guardar_btn = ft.ElevatedButton("Guardar Cambios", on_click=lambda e: self.guardar_cambios_repuesto(e, r))
        volver_btn = ft.ElevatedButton("Volver", on_click=self.volver_al_menu)

        self.page.add(ft.Column([
            ft.Text("Editar Repuesto", size=24, weight="bold"),
            self.id_repuesto, self.nombre, self.descripcion, self.precio, self.stock, self.id_proveedor,
            ft.Row([guardar_btn, volver_btn], spacing=10)
        ], spacing=10))

    def guardar_cambios_repuesto(self, e, r):
        try:
            self.cursor.execute(
                "UPDATE repuesto SET nombre=%s, descripcion=%s, precio=%s, stock=%s, id_proveedor=%s WHERE id_repuesto=%s",
                (self.nombre.value, self.descripcion.value, self.precio.value, self.stock.value, self.id_proveedor.value, self.id_repuesto.value)
            )
            self.connection.commit()
            print("Repuesto actualizado correctamente")
            self.page.snack_bar = ft.SnackBar(ft.Text("Repuesto actualizado correctamente"))
            self.page.snack_bar.open = True
            self.mostrar_repuesto()
        except Exception as ex:
            print(f"Error al actualizar: {ex}")
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al actualizar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def consulta_repuesto(self, e):
        self.page.clean()
        self.data_table = self.create_repuesto_table()
        self.page.add(ft.Text("Consulta de Repuestos", size=24, weight="bold"))
        self.page.add(self.data_table)
        self.page.add(ft.ElevatedButton("Volver", on_click=self.volver_al_menu))

    def imprimir_repuestos(self, e):
        print("Función de impresión no implementada")
        self.page.snack_bar = ft.SnackBar(ft.Text("Función de impresión no implementada"))
        self.page.snack_bar.open = True
        self.page.update()

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback(self.page)
