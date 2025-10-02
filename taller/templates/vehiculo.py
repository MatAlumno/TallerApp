import flet as ft
from db_connection import connect_to_db

class Herramienta_Vehiculo:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None

        self.search_field = ft.TextField(label="Buscar", width=300, on_change=self.search)
        self.search_column = ft.Dropdown(
            options=[
                ft.dropdown.Option("id_ficha"),
                ft.dropdown.Option("marca"),
                ft.dropdown.Option("modelo"),
                ft.dropdown.Option("anio"),
            ],
            value="marca",
            width=200,
            on_change=self.search,
        )
        self.mostrar_vehiculo()

    # Pantalla principal
    def mostrar_vehiculo(self):
        self.page.clean()
        alta_btn = ft.ElevatedButton("Alta", on_click=self.alta)
        consulta_btn = ft.ElevatedButton("Consulta", on_click=self.consulta)
        imprimir_btn = ft.ElevatedButton("Imprimir")
        volver_btn = ft.ElevatedButton("Volver", on_click=lambda e: self.main_menu_callback(self.page))
        self.page.add(ft.Row([alta_btn, consulta_btn, imprimir_btn, volver_btn], alignment=ft.MainAxisAlignment.CENTER))
        self.page.update()

    # Alta de vehículo
    def alta(self, e):
        self.page.clean()
        self.id_cliente = ft.TextField(label="ID Cliente")
        self.marca = ft.TextField(label="Marca")
        self.modelo = ft.TextField(label="Modelo")
        self.anio = ft.TextField(label="Año")
        self.numero_chasis = ft.TextField(label="Número de Chasis")
        self.numero_motor = ft.TextField(label="Número de Motor")

        guardar_btn = ft.ElevatedButton("Guardar", on_click=self.guardar)
        volver_btn = ft.ElevatedButton("Volver", on_click=lambda e: self.mostrar_vehiculo())
        self.page.add(self.id_cliente, self.marca, self.modelo, self.anio, self.numero_chasis, self.numero_motor,
                      ft.Row([guardar_btn, volver_btn]))
        self.page.update()

    def guardar(self, e):
        try:
            query = "INSERT INTO ficha_tecnica (id_cliente, marca, modelo, anio, numero_chasis, numero_motor) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (self.id_cliente.value, self.marca.value, self.modelo.value, self.anio.value, self.numero_chasis.value, self.numero_motor.value)
            self.cursor.execute(query, values)
            self.connection.commit()
            self.page.snack_bar = ft.SnackBar(ft.Text("Vehículo agregado exitosamente"))
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
                ft.DataColumn(ft.Text("Cliente")),
                ft.DataColumn(ft.Text("Marca")),
                ft.DataColumn(ft.Text("Modelo")),
                ft.DataColumn(ft.Text("Año")),
                ft.DataColumn(ft.Text("Nro Chasis")),
                ft.DataColumn(ft.Text("Nro Motor")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]
        )
        volver_btn = ft.ElevatedButton("Volver", on_click=lambda e: self.mostrar_vehiculo())
        self.page.add(ft.Row([self.search_field, self.search_column], alignment=ft.MainAxisAlignment.CENTER))
        self.page.add(self.data_table, volver_btn)
        self.cargar_datos()
        self.page.update()

    def cargar_datos(self, filtro_columna=None, filtro_valor=None):
        self.data_table.rows.clear()
        try:
            query = "SELECT id_ficha, id_cliente, marca, modelo, anio, numero_chasis, numero_motor FROM ficha_tecnica"
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
                            ft.DataCell(ft.Text(str(fila[1]))),
                            ft.DataCell(ft.Text(fila[2])),
                            ft.DataCell(ft.Text(fila[3])),
                            ft.DataCell(ft.Text(str(fila[4]))),
                            ft.DataCell(ft.Text(fila[5])),
                            ft.DataCell(ft.Text(fila[6])),
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

    def editar(self, id_ficha):
        self.cursor.execute("SELECT id_cliente, marca, modelo, anio, numero_chasis, numero_motor FROM ficha_tecnica WHERE id_ficha = %s", (id_ficha,))
        fila = self.cursor.fetchone()
        if not fila: return
        self.page.clean()
        self.id_cliente = ft.TextField(label="ID Cliente", value=str(fila[0]))
        self.marca = ft.TextField(label="Marca", value=fila[1])
        self.modelo = ft.TextField(label="Modelo", value=fila[2])
        self.anio = ft.TextField(label="Año", value=str(fila[3]))
        self.numero_chasis = ft.TextField(label="Nro Chasis", value=fila[4])
        self.numero_motor = ft.TextField(label="Nro Motor", value=fila[5])
        guardar_btn = ft.ElevatedButton("Actualizar", on_click=lambda e: self.actualizar(id_ficha))
        volver_btn = ft.ElevatedButton("Volver", on_click=lambda e: self.consulta(None))
        self.page.add(self.id_cliente, self.marca, self.modelo, self.anio, self.numero_chasis, self.numero_motor,
                      ft.Row([guardar_btn, volver_btn]))
        self.page.update()

    def actualizar(self, id_ficha):
        try:
            query = "UPDATE ficha_tecnica SET id_cliente=%s, marca=%s, modelo=%s, anio=%s, numero_chasis=%s, numero_motor=%s WHERE id_ficha=%s"
            values = (self.id_cliente.value, self.marca.value, self.modelo.value, self.anio.value, self.numero_chasis.value, self.numero_motor.value, id_ficha)
            self.cursor.execute(query, values)
            self.connection.commit()
            self.page.snack_bar = ft.SnackBar(ft.Text("Vehículo actualizado exitosamente"))
            self.page.snack_bar.open = True
            self.consulta(None)
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al actualizar: {ex}"))
            self.page.snack_bar.open = True
        self.page.update()

    def eliminar(self, id_ficha):
        try:
            self.cursor.execute("DELETE FROM ficha_tecnica WHERE id_ficha = %s", (id_ficha,))
            self.connection.commit()
            self.page.snack_bar = ft.SnackBar(ft.Text("Vehículo eliminado"))
            self.page.snack_bar.open = True
            self.consulta(None)
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar: {ex}"))
            self.page.snack_bar.open = True
        self.page.update()

    def search(self, e):
        self.cargar_datos(self.search_column.value, self.search_field.value)
