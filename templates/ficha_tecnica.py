import flet as ft
from db import connect_to_db

class Pagina_FichaTecnica:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None
        self.search_field = ft.TextField(label="Buscar", width=300, on_change=self.search)
        self.search_column = ft.Dropdown(
            options=[
                ft.dropdown.Option("id_ficha", text="ID Ficha"),
                ft.dropdown.Option("id_cliente", text="ID Cliente"),
                ft.dropdown.Option("marca", text="Marca"),
                ft.dropdown.Option("modelo", text="Modelo"),
                ft.dropdown.Option("anio", text="Año"),
                ft.dropdown.Option("numero_chasis", text="Nro Chasis"),
                ft.dropdown.Option("numero_motor", text="Nro Motor"),
            ],
            value="id_ficha",
            width=200,
            on_change=self.search,
        )
        self.all_data = []
        self.mostrar_ficha_tecnica()

    def mostrar_ficha_tecnica(self):
        self.page.clean()
        header = ft.Row(
            controls=[
                ft.Text("Gestión de Fichas Técnicas", size=20, weight="bold"),
                ft.ElevatedButton("Alta", on_click=self.alta_ficha_tecnica),
                ft.ElevatedButton("Consulta", on_click=self.consulta_ficha_tecnica),
                ft.ElevatedButton("Imprimir", on_click=self.imprimir_fichas_tecnicas),
                ft.ElevatedButton("Volver al Menú", on_click=self.volver_al_menu),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        search_row = ft.Row([self.search_column, self.search_field], alignment=ft.MainAxisAlignment.START)
        self.data_table = self.create_ficha_tecnica_table()
        self.page.add(
            ft.Container(
                content=ft.Column([header, search_row, self.data_table], spacing=10),
                padding=20
            )
        )

    def alta_ficha_tecnica(self, e):
        self.page.clean()
        self.id_cliente = ft.TextField(label="ID Cliente", width=300)
        self.marca = ft.TextField(label="Marca", width=300)
        self.modelo = ft.TextField(label="Modelo", width=300)
        self.anio = ft.TextField(label="Año", width=300)
        self.numero_chasis = ft.TextField(label="Nro Chasis", width=300)
        self.numero_motor = ft.TextField(label="Nro Motor", width=300)

        guardar_btn = ft.ElevatedButton("Guardar", on_click=self.guardar_ficha_tecnica)
        volver_btn = ft.ElevatedButton("Volver", on_click=self.volver_al_menu)

        self.page.add(
            ft.Column([
                ft.Text("Alta de Ficha Técnica", size=24, weight="bold"),
                self.id_cliente, self.marca, self.modelo, self.anio, self.numero_chasis, self.numero_motor,
                ft.Row([guardar_btn, volver_btn], spacing=10)
            ], spacing=10)
        )

    def guardar_ficha_tecnica(self, e):
        if not self.cursor:
            return
        try:
            self.cursor.execute(
                "INSERT INTO ficha_tecnica (id_cliente, marca, modelo, anio, numero_chasis, numero_motor) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (self.id_cliente.value, self.marca.value, self.modelo.value,
                 self.anio.value, self.numero_chasis.value, self.numero_motor.value)
            )
            self.connection.commit()
            self.page.snack_bar = ft.SnackBar(ft.Text("Ficha técnica guardada correctamente"))
            self.page.snack_bar.open = True
            self.mostrar_ficha_tecnica()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al guardar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def create_ficha_tecnica_table(self):
        if not self.cursor:
            return ft.Text("No hay conexión a la base de datos")
        try:
            self.cursor.execute(
                "SELECT id_ficha, id_cliente, marca, modelo, anio, numero_chasis, numero_motor "
                "FROM ficha_tecnica ORDER BY id_ficha"
            )
            datos = self.cursor.fetchall()
            self.all_data = datos
            rows = []
            for f in datos:
                eliminar_btn = ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar",
                                             on_click=lambda e, ficha=f: self.eliminar_ficha_tecnica(e, ficha))
                actualizar_btn = ft.IconButton(icon=ft.Icons.EDIT, tooltip="Actualizar",
                                               on_click=lambda e, ficha=f: self.actualizar_ficha_tecnica(e, ficha))
                rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(f[0]))),
                    ft.DataCell(ft.Text(str(f[1]))),
                    ft.DataCell(ft.Text(f[2])),
                    ft.DataCell(ft.Text(f[3])),
                    ft.DataCell(ft.Text(str(f[4]))),
                    ft.DataCell(ft.Text(f[5])),
                    ft.DataCell(ft.Text(f[6])),
                    ft.DataCell(ft.Row([eliminar_btn, actualizar_btn]))
                ]))
            return ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID Ficha")),
                    ft.DataColumn(ft.Text("ID Cliente")),
                    ft.DataColumn(ft.Text("Marca")),
                    ft.DataColumn(ft.Text("Modelo")),
                    ft.DataColumn(ft.Text("Año")),
                    ft.DataColumn(ft.Text("Nro Chasis")),
                    ft.DataColumn(ft.Text("Nro Motor")),
                    ft.DataColumn(ft.Text("Acciones")),
                ],
                rows=rows
            )
        except Exception as ex:
            return ft.Text(f"Error al cargar fichas: {ex}")

    def search(self, e):
        term = self.search_field.value.lower()
        col_index = self.get_column_index(self.search_column.value)
        filtered = [f for f in self.all_data if term in str(f[col_index]).lower()]
        self.data_table.rows = self.get_rows(filtered)
        self.page.update()

    def get_column_index(self, column_name):
        mapping = {
            "id_ficha": 0,
            "id_cliente": 1,
            "marca": 2,
            "modelo": 3,
            "anio": 4,
            "numero_chasis": 5,
            "numero_motor": 6
        }
        return mapping.get(column_name, 0)

    def get_rows(self, fichas):
        rows = []
        for f in fichas:
            eliminar_btn = ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar",
                                         on_click=lambda e, ficha=f: self.eliminar_ficha_tecnica(e, ficha))
            actualizar_btn = ft.IconButton(icon=ft.Icons.EDIT, tooltip="Actualizar",
                                           on_click=lambda e, ficha=f: self.actualizar_ficha_tecnica(e, ficha))
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(f[0]))),
                ft.DataCell(ft.Text(str(f[1]))),
                ft.DataCell(ft.Text(f[2])),
                ft.DataCell(ft.Text(f[3])),
                ft.DataCell(ft.Text(str(f[4]))),
                ft.DataCell(ft.Text(f[5])),
                ft.DataCell(ft.Text(f[6])),
                ft.DataCell(ft.Row([eliminar_btn, actualizar_btn]))
            ]))
        return rows

    def eliminar_ficha_tecnica(self, e, ficha):
        try:
            self.cursor.execute("DELETE FROM ficha_tecnica WHERE id_ficha=%s", (ficha[0],))
            self.connection.commit()
            self.page.snack_bar = ft.SnackBar(ft.Text("Ficha técnica eliminada correctamente"))
            self.page.snack_bar.open = True
            self.mostrar_ficha_tecnica()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def actualizar_ficha_tecnica(self, e, ficha):
        self.page.clean()
        self.id_ficha = ft.TextField(label="ID Ficha", value=str(ficha[0]), width=300, disabled=True)
        self.id_cliente = ft.TextField(label="ID Cliente", value=str(ficha[1]), width=300)
        self.marca = ft.TextField(label="Marca", value=ficha[2], width=300)
        self.modelo = ft.TextField(label="Modelo", value=ficha[3], width=300)
        self.anio = ft.TextField(label="Año", value=str(ficha[4]), width=300)
        self.numero_chasis = ft.TextField(label="Nro Chasis", value=ficha[5], width=300)
        self.numero_motor = ft.TextField(label="Nro Motor", value=ficha[6], width=300)


    def guardar_cambios_ficha_tecnica(self, e, ficha):
        try:
            self.cursor.execute(
                "UPDATE ficha_tecnica SET id_cliente=%s, marca=%s, modelo=%s, anio=%s, numero_chasis=%s, numero_motor=%s "
                "WHERE id_ficha=%s",
                (
                    self.id_cliente.value,
                    self.marca.value,
                    self.modelo.value,
                    self.anio.value,
                    self.numero_chasis.value,
                    self.numero_motor.value,
                    self.id_ficha.value
                )
            )
            self.connection.commit()
            self.page.snack_bar = ft.SnackBar(ft.Text("Ficha técnica actualizada correctamente"))
            self.page.snack_bar.open = True
            self.mostrar_ficha_tecnica()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al actualizar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()


    def consulta_ficha_tecnica(self, e):
        self.page.clean()
        self.page.add(ft.Text("Consulta de Fichas Técnicas", size=24, weight="bold"))
        self.page.add(self.create_ficha_tecnica_table())
        self.page.add(ft.ElevatedButton("Volver", on_click=self.volver_al_menu))

    def imprimir_fichas_tecnicas(self, e):
        try:
            self.page.snack_bar = ft.SnackBar(ft.Text("Función de impresión no implementada aún"))
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al imprimir: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()
    
    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback(self.page)