import flet as ft
from db import connect_to_db  

class Pagina_Presupuesto:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None
        self.search_field = ft.TextField(label="Buscar", width=300, on_change=self.search)
        self.search_column = ft.Dropdown(
            options=[
                ft.dropdown.Option("id_presupuesto", text="Id Presupuesto"),
                ft.dropdown.Option("id_ficha", text="Id Ficha"),
                ft.dropdown.Option("fecha", text="Fecha"),
                ft.dropdown.Option("total", text="Total"),
            ],
            value="id_presupuesto",
            width=200,
            on_change=self.search,
        )
        self.all_data = []
        self.mostrar_presupuesto()

    def mostrar_presupuesto(self):
        self.page.clean()
        header = ft.Row(
            controls=[
                ft.Text("Gestión de Presupuestos", size=20, weight="bold"),
                ft.ElevatedButton("Alta", on_click=self.alta_presupuesto),
                ft.ElevatedButton("Consulta", on_click=self.consulta_presupuesto),
                ft.ElevatedButton("Imprimir", on_click=self.imprimir_presupuestos),
                ft.ElevatedButton("Volver al Menú", on_click=self.volver_al_menu),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        search_row = ft.Row([self.search_column, self.search_field], alignment=ft.MainAxisAlignment.START)
        self.data_table, total_presupuesto = self.create_presupuesto_table()
        self.page.add(
            ft.Container(
                content=ft.Column([
                    header,
                    search_row,
                    ft.Text(f"Total General: ${total_presupuesto}", size=16, weight="bold"),
                    self.data_table
                ], spacing=10),
                padding=20
            )
        )

    def alta_presupuesto(self, e):
        self.page.clean()
        self.id_presupuesto = ft.TextField(label="Id Presupuesto", width=300)
        self.id_ficha = ft.TextField(label="Id Ficha", width=300)
        self.fecha = ft.TextField(label="Fecha YYYY-MM-DD", width=300)
        self.total = ft.TextField(label="Total", width=300)

        guardar_btn = ft.ElevatedButton("Guardar", on_click=self.guardar_presupuesto)
        volver_btn = ft.ElevatedButton("Volver", on_click=self.volver_al_menu)

        self.page.add(ft.Column([
            ft.Text("Alta de Presupuesto", size=24, weight="bold"),
            self.id_presupuesto,
            self.id_ficha,
            self.fecha,
            self.total,
            ft.Row([guardar_btn, volver_btn], spacing=10)
        ], spacing=10))

    def guardar_presupuesto(self, e):
        if not self.cursor:
            return
        try:
            self.cursor.execute(
                "INSERT INTO presupuesto (id_presupuesto, id_ficha, fecha, total) VALUES (%s,%s,%s,%s)",
                (self.id_presupuesto.value, self.id_ficha.value, self.fecha.value, self.total.value)
            )
            self.connection.commit()
            print("Presupuesto guardado correctamente")
            self.page.snack_bar = ft.SnackBar(ft.Text("Presupuesto guardado correctamente"))
            self.page.snack_bar.open = True
            self.mostrar_presupuesto()
        except Exception as ex:
            print(f"Error al guardar: {ex}")
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al guardar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def create_presupuesto_table(self, data=None):
        if not self.cursor:
            return ft.Text("No hay conexión a la base de datos"), 0

        if data is None:
            self.cursor.execute(
                "SELECT id_presupuesto, id_ficha, fecha, total FROM presupuesto ORDER BY id_presupuesto"
            )
            datos_presupuestos = self.cursor.fetchall()
        else:
            datos_presupuestos = data

        self.all_data = datos_presupuestos
        rows = []
        total_general = 0

        for p in datos_presupuestos:
            total_general += float(p[3] or 0)
            eliminar_btn = ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar",
                                         on_click=lambda e, x=p: self.eliminar_presupuesto(e, x))
            actualizar_btn = ft.IconButton(icon=ft.Icons.EDIT, tooltip="Actualizar",
                                           on_click=lambda e, x=p: self.actualizar_presupuesto(e, x))
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(p[0]))),  
                ft.DataCell(ft.Text(str(p[1]))),  
                ft.DataCell(ft.Text(str(p[2]))),  
                ft.DataCell(ft.Text(str(p[3]))),  
                ft.DataCell(ft.Row([eliminar_btn, actualizar_btn]))
            ]))

        data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Id Presupuesto")),
                ft.DataColumn(ft.Text("Id Ficha")),
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("Total")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=rows
        )
        return data_table, total_general

    def eliminar_presupuesto(self, e, p):
        try:
            self.cursor.execute("DELETE FROM presupuesto WHERE id_presupuesto=%s", (p[0],))
            self.connection.commit()
            print("Presupuesto eliminado correctamente")
            self.page.snack_bar = ft.SnackBar(ft.Text("Presupuesto eliminado correctamente"))
            self.page.snack_bar.open = True
            self.mostrar_presupuesto()
        except Exception as ex:
            print(f"Error al eliminar: {ex}")
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def actualizar_presupuesto(self, e, p):
        self.page.clean()
        self.id_presupuesto = ft.TextField(label="Id Presupuesto", value=str(p[0]), width=300, disabled=True)
        self.id_ficha = ft.TextField(label="Id Ficha", value=str(p[1]), width=300)
        self.fecha = ft.TextField(label="Fecha", value=str(p[2]), width=300)
        self.total = ft.TextField(label="Total", value=str(p[3]), width=300)

        guardar_btn = ft.ElevatedButton("Guardar Cambios", on_click=lambda e: self.guardar_cambios_presupuesto(e, p))
        volver_btn = ft.ElevatedButton("Volver", on_click=self.volver_al_menu)

        self.page.add(ft.Column([
            ft.Text("Editar Presupuesto", size=24, weight="bold"),
            self.id_presupuesto, self.id_ficha, self.fecha, self.total,
            ft.Row([guardar_btn, volver_btn], spacing=10)
        ], spacing=10))

    def guardar_cambios_presupuesto(self, e, p):
        try:
            self.cursor.execute(
                "UPDATE presupuesto SET id_ficha=%s, fecha=%s, total=%s WHERE id_presupuesto=%s",
                (self.id_ficha.value, self.fecha.value, self.total.value, self.id_presupuesto.value)
            )
            self.connection.commit()
            print("Presupuesto actualizado correctamente")
            self.page.snack_bar = ft.SnackBar(ft.Text("Presupuesto actualizado correctamente"))
            self.page.snack_bar.open = True
            self.mostrar_presupuesto()
        except Exception as ex:
            print(f"Error al actualizar: {ex}")
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al actualizar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def search(self, e):
        term = self.search_field.value.lower()
        col = self.search_column.value
        filtered = []

        for row in self.all_data:
            if col == "id_presupuesto" and term in str(row[0]).lower():
                filtered.append(row)
            elif col == "id_ficha" and term in str(row[1]).lower():
                filtered.append(row)
            elif col == "fecha" and term in str(row[2]).lower():
                filtered.append(row)
            elif col == "total" and term in str(row[3]).lower():
                filtered.append(row)

        self.data_table, total_general = self.create_presupuesto_table(filtered)
        self.page.update()

    def consulta_presupuesto(self, e):
        self.page.clean()
        self.data_table, total_general = self.create_presupuesto_table()
        self.page.add(ft.Text("Consulta de Presupuestos", size=24, weight="bold"))
        self.page.add(ft.Text(f"Total General: ${total_general}", size=16, weight="bold"))
        self.page.add(self.data_table)
        self.page.add(ft.ElevatedButton("Volver", on_click=self.volver_al_menu))

    def imprimir_presupuestos(self, e):
        print("Función de impresión no implementada")
        self.page.snack_bar = ft.SnackBar(ft.Text("Función de impresión no implementada"))
        self.page.snack_bar.open = True
        self.page.update()

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback(self.page)
