import flet as ft
from db import connect_to_db  

class Pagina_Proveedor:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None
        self.search_field = ft.TextField(label="Buscar", width=300, on_change=self.search)
        self.search_column = ft.Dropdown(
            options=[
                ft.dropdown.Option("id_proveedor", text="ID Proveedor"),
                ft.dropdown.Option("dni", text="DNI"),
                ft.dropdown.Option("nombre_empresa", text="Nombre Empresa"),
            ],
            value="nombre_empresa",
            width=200,
            on_change=self.search,
        )
        self.all_data = []
        self.mostrar_proveedor()

    def mostrar_proveedor(self):
        self.page.clean()
        header = ft.Row(
            controls=[
                ft.Text("Gestión de Proveedores", size=20, weight="bold"),
                ft.ElevatedButton("Alta", on_click=self.alta_proveedor),
                ft.ElevatedButton("Consulta", on_click=self.consulta_proveedor),
                ft.ElevatedButton("Imprimir", on_click=self.imprimir_proveedores),
                ft.ElevatedButton("Volver al Menú", on_click=self.volver_al_menu),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        search_row = ft.Row([self.search_column, self.search_field], alignment=ft.MainAxisAlignment.START)
        self.data_table = self.create_proveedor_table()
        self.page.add(
            ft.Container(
                content=ft.Column([header, search_row, self.data_table], spacing=10),
                padding=20
            )
        )

    def alta_proveedor(self, e):
        self.page.clean()
        self.dni = ft.TextField(label="DNI", width=300)
        self.nombre_empresa = ft.TextField(label="Nombre Empresa", width=300)

        guardar_btn = ft.ElevatedButton("Guardar", on_click=self.guardar_proveedor)
        volver_btn = ft.ElevatedButton("Volver", on_click=self.volver_al_menu)

        self.page.add(ft.Column([
            ft.Text("Alta de Proveedor", size=24, weight="bold"),
            self.dni, self.nombre_empresa,
            ft.Row([guardar_btn, volver_btn], spacing=10)
        ], spacing=10))

    def guardar_proveedor(self, e):
        if not self.cursor:
            return
        try:
            self.cursor.execute(
                "INSERT INTO proveedor (dni, nombre_empresa) VALUES (%s, %s)",
                (self.dni.value, self.nombre_empresa.value)
            )
            self.connection.commit()
            print("Proveedor guardado correctamente")
            self.page.snack_bar = ft.SnackBar(ft.Text("Proveedor guardado correctamente"))
            self.page.snack_bar.open = True
            self.mostrar_proveedor()
        except Exception as ex:
            print(f"Error al guardar: {ex}")
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al guardar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def create_proveedor_table(self):
        if not self.cursor:
            return ft.Text("No hay conexión a la base de datos")
        self.cursor.execute("SELECT id_proveedor, dni, nombre_empresa FROM proveedor ORDER BY nombre_empresa")
        self.all_data = self.cursor.fetchall()
        rows = self.get_rows(self.all_data)
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID Proveedor")),
                ft.DataColumn(ft.Text("DNI")),
                ft.DataColumn(ft.Text("Nombre Empresa")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=rows
        )

    def get_rows(self, proveedores):
        rows = []
        for p in proveedores:
            eliminar_btn = ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar", on_click=lambda e, x=p: self.eliminar_proveedor(e, x))
            actualizar_btn = ft.IconButton(icon=ft.Icons.EDIT, tooltip="Modificar", on_click=lambda e, x=p: self.actualizar_proveedor(e, x))
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(p[0]))), 
                ft.DataCell(ft.Text(p[1])),       
                ft.DataCell(ft.Text(p[2])),       
                ft.DataCell(ft.Row([eliminar_btn, actualizar_btn]))
            ]))
        return rows

    def search(self, e):
        term = self.search_field.value.lower()
        col = self.search_column.value
        filtered = []
        for row in self.all_data:
            if col == "id_proveedor" and term in str(row[0]).lower():
                filtered.append(row)
            elif col == "dni" and term in str(row[1]).lower():
                filtered.append(row)
            elif col == "nombre_empresa" and term in row[2].lower():
                filtered.append(row)
        self.data_table.rows = self.get_rows(filtered)
        self.page.update()

    def eliminar_proveedor(self, e, p):
        try:
            self.cursor.execute("DELETE FROM proveedor WHERE id_proveedor=%s", (p[0],))
            self.connection.commit()
            print("Proveedor eliminado correctamente")
            self.page.snack_bar = ft.SnackBar(ft.Text("Proveedor eliminado correctamente"))
            self.page.snack_bar.open = True
            self.mostrar_proveedor()
        except Exception as ex:
            print(f"Error al eliminar: {ex}")
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def actualizar_proveedor(self, e, p):
        self.page.clean()
        self.id_proveedor = ft.TextField(label="ID Proveedor", value=str(p[0]), width=300, disabled=True)
        self.dni = ft.TextField(label="DNI", value=p[1], width=300)
        self.nombre_empresa = ft.TextField(label="Nombre Empresa", value=p[2], width=300)

        guardar_btn = ft.ElevatedButton("Guardar Cambios", on_click=lambda e: self.guardar_cambios_proveedor(e, p))
        volver_btn = ft.ElevatedButton("Volver", on_click=self.volver_al_menu)

        self.page.add(ft.Column([
            ft.Text("Editar Proveedor", size=24, weight="bold"),
            self.id_proveedor, self.dni, self.nombre_empresa,
            ft.Row([guardar_btn, volver_btn], spacing=10)
        ], spacing=10))

    def guardar_cambios_proveedor(self, e, p):
        try:
            self.cursor.execute(
                "UPDATE proveedor SET dni=%s, nombre_empresa=%s WHERE id_proveedor=%s",
                (self.dni.value, self.nombre_empresa.value, self.id_proveedor.value)
            )
            self.connection.commit()
            print("Proveedor actualizado correctamente")
            self.page.snack_bar = ft.SnackBar(ft.Text("Proveedor actualizado correctamente"))
            self.page.snack_bar.open = True
            self.mostrar_proveedor()
        except Exception as ex:
            print(f"Error al actualizar: {ex}")
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al actualizar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def consulta_proveedor(self, e):
        self.page.clean()
        self.data_table = self.create_proveedor_table()
        self.page.add(ft.Text("Consulta de Proveedores", size=24, weight="bold"))
        self.page.add(self.data_table)
        self.page.add(ft.ElevatedButton("Volver", on_click=self.volver_al_menu))

    def imprimir_proveedores(self, e):
        print("Función de impresión no implementada")
        self.page.snack_bar = ft.SnackBar(ft.Text("Función de impresión no implementada"))
        self.page.snack_bar.open = True
        self.page.update()

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback(self.page)

'''import flet as ft
from db import connect_to_db

def proveedor_page(page: ft.Page):
    container = ft.View()
    dt = ft.DataTable(
        columns=[ft.DataColumn(ft.Text("Cod Proveedor")), ft.DataColumn(ft.Text("Nombre"))],
        rows=[]
    )

    def load_data():
        dt.rows.clear()
        db = connect_to_db()
        cursor = db.cursor()
        cursor.execute("SELECT cod_proveedor, nombre FROM proveedor")
        for cod, nombre in cursor.fetchall():
            dt.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(cod)), ft.DataCell(ft.Text(nombre))]))
        db.close()
        page.update()

    def add_proveedor(e):
        db = connect_to_db()
        cursor = db.cursor()
        cod = f"P{ft.time.time_ns()%10000}"
        nombre = "Proveedor X"
        cursor.execute("INSERT INTO proveedor (cod_proveedor,nombre) VALUES (%s,%s)", (cod,nombre))
        db.commit()
        db.close()
        load_data()

    container.controls.extend([
        dt,
        ft.Row([ft.ElevatedButton("Agregar", on_click=add_proveedor),
                ft.ElevatedButton("Volver", on_click=lambda e: page.views.pop())])
    ])
    load_data()
    return container
'''