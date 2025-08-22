import flet as ft
from db import connect_to_db

class Pagina_Empleado:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None
        self.search_field = ft.TextField(label="Buscar", width=300, on_change=self.search)
        self.search_column = ft.Dropdown(
            options=[
                ft.dropdown.Option("id_empleado", text="ID"),
                ft.dropdown.Option("dni", text="DNI"),
                ft.dropdown.Option("apellido", text="Apellido"),
                ft.dropdown.Option("nombre", text="Nombre"),
                ft.dropdown.Option("puesto", text="Puesto"),
                ft.dropdown.Option("salario", text="Salario"),
            ],
            value="id_empleado",
            width=200,
            on_change=self.search,
        )
        self.all_data = []
        self.mostrar_empleado()

    def mostrar_empleado(self):
        self.page.clean()
        header = ft.Row(
            controls=[
                ft.Text("Gestión de Empleados", size=20, weight="bold"),
                ft.ElevatedButton("Alta", on_click=self.alta_empleado),
                ft.ElevatedButton("Consulta", on_click=self.consulta_empleado),
                ft.ElevatedButton("Imprimir", on_click=self.imprimir_empleados),
                ft.ElevatedButton("Volver al Menú", on_click=self.volver_al_menu),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        search_row = ft.Row([self.search_column, self.search_field], alignment=ft.MainAxisAlignment.START)
        self.data_table = self.create_empleado_table()
        self.page.add(
            ft.Container(
                content=ft.Column([header, search_row, self.data_table], spacing=10),
                padding=20
            )
        )

    def alta_empleado(self, e):
        self.page.clean()
        self.dni = ft.TextField(label="DNI", width=300)
        self.nombre = ft.TextField(label="Nombre", width=300)
        self.apellido = ft.TextField(label="Apellido", width=300)
        self.direccion = ft.TextField(label="Dirección", width=300)
        self.telefono = ft.TextField(label="Teléfono", width=300)
        self.puesto = ft.TextField(label="Puesto", width=300)
        self.salario = ft.TextField(label="Salario", width=300)
        self.fecha_contratacion = ft.TextField(label="Fecha Contratación (YYYY-MM-DD)", width=300)

        guardar_btn = ft.ElevatedButton("Guardar", on_click=self.guardar_empleado)
        volver_btn = ft.ElevatedButton("Volver", on_click=self.mostrar_empleado)

        self.page.add(
            ft.Column([
                ft.Text("Alta de Empleado", size=24, weight="bold"),
                self.dni, self.nombre, self.apellido, self.direccion, self.telefono,
                self.puesto, self.salario, self.fecha_contratacion,
                ft.Row([guardar_btn, volver_btn], spacing=10)
            ], spacing=10)
        )

    def guardar_empleado(self, e):
        if not self.cursor:
            return
        try:
            # Insertar en persona
            self.cursor.execute(
                "INSERT INTO persona (dni, nombre, apellido, direccion, telefono) VALUES (%s,%s,%s,%s,%s)",
                (self.dni.value, self.nombre.value, self.apellido.value, self.direccion.value, self.telefono.value)
            )
            # Insertar en empleado
            self.cursor.execute(
                "INSERT INTO empleado (dni, puesto, salario, fecha_contratacion) VALUES (%s,%s,%s,%s)",
                (self.dni.value, self.puesto.value, self.salario.value, self.fecha_contratacion.value)
            )
            self.connection.commit()
            print("Empleado guardado correctamente")
            self.page.snack_bar = ft.SnackBar(ft.Text("Empleado guardado correctamente"))
            self.page.snack_bar.open = True
            self.mostrar_empleado()
        except Exception as ex:
            print(f"Error al guardar: {ex}")
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al guardar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def create_empleado_table(self):
        if not self.cursor:
            return ft.Text("No hay conexión a la base de datos")
        try:
            self.cursor.execute("""
                SELECT e.id_empleado, p.dni, p.apellido, p.nombre, p.direccion, p.telefono, e.puesto, e.salario, e.fecha_contratacion
                FROM empleado e
                JOIN persona p ON e.dni = p.dni
                ORDER BY e.id_empleado
            """)
            datos = self.cursor.fetchall()
            self.all_data = datos
            rows = []
            for emp in datos:
                eliminar_btn = ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar", on_click=lambda e, empleado=emp: self.eliminar_empleado(e, empleado))
                actualizar_btn = ft.IconButton(icon=ft.Icons.EDIT, tooltip="Actualizar", on_click=lambda e, empleado=emp: self.actualizar_empleado(e, empleado))
                rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(emp[0]))),  # id_empleado
                    ft.DataCell(ft.Text(str(emp[1]))),  # dni
                    ft.DataCell(ft.Text(emp[2])),       # apellido
                    ft.DataCell(ft.Text(emp[3])),       # nombre
                    ft.DataCell(ft.Text(emp[4])),       # direccion
                    ft.DataCell(ft.Text(emp[5])),       # telefono
                    ft.DataCell(ft.Text(emp[6])),       # puesto
                    ft.DataCell(ft.Text(str(emp[7]))),  # salario
                    ft.DataCell(ft.Text(str(emp[8]))),  # fecha_contratacion
                    ft.DataCell(ft.Row([eliminar_btn, actualizar_btn]))
                ]))
            return ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("DNI")), ft.DataColumn(ft.Text("Apellido")),
                    ft.DataColumn(ft.Text("Nombre")), ft.DataColumn(ft.Text("Dirección")), ft.DataColumn(ft.Text("Teléfono")),
                    ft.DataColumn(ft.Text("Puesto")), ft.DataColumn(ft.Text("Salario")), ft.DataColumn(ft.Text("Fecha Contratación")),
                    ft.DataColumn(ft.Text("Acciones"))
                ],
                rows=rows
            )
        except Exception as ex:
            return ft.Text(f"Error al cargar empleados: {ex}")

    def search(self, e):
        term = self.search_field.value.lower()
        col = self.search_column.value
        filtered = []
        for row in self.all_data:
            if col == "id_empleado" and term in str(row[0]).lower():
                filtered.append(row)
            elif col == "dni" and term in str(row[1]).lower():
                filtered.append(row)
            elif col == "apellido" and term in row[2].lower():
                filtered.append(row)
            elif col == "nombre" and term in row[3].lower():
                filtered.append(row)
            elif col == "puesto" and term in row[6].lower():
                filtered.append(row)
            elif col == "salario" and term in str(row[7]).lower():
                filtered.append(row)
        self.data_table.rows = self.get_rows(filtered)
        self.page.update()

    def get_rows(self, empleados):
        rows = []
        for emp in empleados:
            eliminar_btn = ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar", on_click=lambda e, empleado=emp: self.eliminar_empleado(e, empleado))
            actualizar_btn = ft.IconButton(icon=ft.Icons.EDIT, tooltip="Actualizar", on_click=lambda e, empleado=emp: self.actualizar_empleado(e, emp))
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(emp[0]))),
                ft.DataCell(ft.Text(str(emp[1]))),
                ft.DataCell(ft.Text(emp[2])),
                ft.DataCell(ft.Text(emp[3])),
                ft.DataCell(ft.Text(emp[4])),
                ft.DataCell(ft.Text(emp[5])),
                ft.DataCell(ft.Text(emp[6])),
                ft.DataCell(ft.Text(str(emp[7]))),
                ft.DataCell(ft.Text(str(emp[8]))),
                ft.DataCell(ft.Row([eliminar_btn, actualizar_btn]))
            ]))
        return rows

    def eliminar_empleado(self, e, emp):
        try:
            dni = emp[1]
            id_empleado = emp[0]
            self.cursor.execute("DELETE FROM empleado WHERE id_empleado=%s", (id_empleado,))
            self.cursor.execute("DELETE FROM persona WHERE dni=%s", (dni,))
            self.connection.commit()
            print("Empleado eliminado correctamente")
            self.page.snack_bar = ft.SnackBar(ft.Text("Empleado eliminado correctamente"))
            self.page.snack_bar.open = True
            self.mostrar_empleado()
        except Exception as ex:
            print(f"Error al eliminar: {ex}")
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def actualizar_empleado(self, e, emp):
        self.page.clean()
        self.id_empleado = ft.TextField(label="ID", value=str(emp[0]), width=300, disabled=True)
        self.dni = ft.TextField(label="DNI", value=str(emp[1]), width=300)
        self.apellido = ft.TextField(label="Apellido", value=emp[2], width=300)
        self.nombre = ft.TextField(label="Nombre", value=emp[3], width=300)
        self.direccion = ft.TextField(label="Dirección", value=emp[4], width=300)
        self.telefono = ft.TextField(label="Teléfono", value=emp[5], width=300)
        self.puesto = ft.TextField(label="Puesto", value=emp[6], width=300)
        self.salario = ft.TextField(label="Salario", value=str(emp[7]), width=300)
        self.fecha_contratacion = ft.TextField(label="Fecha Contratación YYYY-MM-DD", value=str(emp[8]), width=300)

        guardar_btn = ft.ElevatedButton("Guardar Cambios", on_click=lambda e: self.guardar_cambios_empleado(e, emp))
        volver_btn = ft.ElevatedButton("Volver", on_click=self.mostrar_empleado)

        self.page.add(
            ft.Column([self.id_empleado, self.dni, self.apellido, self.nombre, self.direccion, self.telefono,
                       self.puesto, self.salario, self.fecha_contratacion,
                       ft.Row([guardar_btn, volver_btn], spacing=10)], spacing=10)
        )

    def guardar_cambios_empleado(self, e, emp):
        try:
            self.cursor.execute(
                "UPDATE persona SET nombre=%s, apellido=%s, direccion=%s, telefono=%s WHERE dni=%s",
                (self.nombre.value, self.apellido.value, self.direccion.value, self.telefono.value, self.dni.value)
            )
            self.cursor.execute(
                "UPDATE empleado SET puesto=%s, salario=%s, fecha_contratacion=%s WHERE id_empleado=%s",
                (self.puesto.value, self.salario.value, self.fecha_contratacion.value, emp[0])
            )
            self.connection.commit()
            print("Empleado actualizado correctamente")
            self.page.snack_bar = ft.SnackBar(ft.Text("Empleado actualizado correctamente"))
            self.page.snack_bar.open = True
            self.mostrar_empleado()
        except Exception as ex:
            print(f"Error al actualizar: {ex}")
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al actualizar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def consulta_empleado(self, e):
        self.page.clean()
        self.page.add(ft.Text("Consulta de Empleados", size=24, weight="bold"))
        self.page.add(self.create_empleado_table())
        self.page.add(ft.ElevatedButton("Volver", on_click=self.mostrar_empleado))
        self.page.update()

    def imprimir_empleados(self, e):
        try:
            print("Función de impresión no implementada")
            self.page.snack_bar = ft.SnackBar(ft.Text("Función de impresión no implementada"))
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as ex:
            print(f"Error al imprimir: {ex}")
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al imprimir: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback(self.page) 



'''import flet as ft
import mysql.connector

def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="NikoStasyszyn",
            database="taller_mecanico",
            ssl_disabled=True,
        )
        if connection.is_connected():
            print("Conexión exitosa")
            return connection
    except Exception as ex:
        print("Conexión errónea")
        print(ex)
        return None

class Herramienta_Empleado:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None
        self.search_field = ft.TextField(label="Buscar", width=300, on_change=self.search)
        self.search_column = ft.Dropdown(
            options=[
                ft.dropdown.Option("legajo"),
                ft.dropdown.Option("apellido"),
                ft.dropdown.Option("nombre"),
                ft.dropdown.Option("dni"),
                ft.dropdown.Option("direccion"),
                ft.dropdown.Option("telefono"),
            ],
            value="apellido",
            width=200,
            on_change=self.search,
        )
        self.mostrar_empleado()

    def mostrar_empleado(self):
        self.page.clean()
        header = ft.Row(
            controls=[
                ft.Text("Gestión de Empleados", size=20, weight="bold"),
                ft.ElevatedButton(text="Alta", on_click=self.alta_empleado),
                ft.ElevatedButton(text="Consulta", on_click=self.consulta_empleado),
                ft.ElevatedButton(text="Imprimir", on_click=self.imprimir_empleados),
                ft.ElevatedButton(text="Volver al Menú", on_click=self.volver_al_menu),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        search_row = ft.Row(
            [
                self.search_column,
                self.search_field,
            ],
            alignment=ft.MainAxisAlignment.START,
        )
        self.data_table = self.create_empleado_table()
        self.page.add(
            ft.Container(
                content=ft.Column(
                    controls=[header, search_row, self.data_table],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
            )
        )

    def alta_empleado(self, e):
        self.page.clean()
        self.legajo = ft.TextField(label="Legajo", width=300)
        self.dni = ft.TextField(label="DNI", width=300)
        self.apellido = ft.TextField(label="Apellido", width=300)
        self.nombre = ft.TextField(label="Nombre", width=300)
        self.direccion = ft.TextField(label="Dirección", width=300)
        self.telefono = ft.TextField(label="Teléfono", width=300)

        guardar_btn = ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=self.guardar_empleado)
        volver_btn = ft.ElevatedButton("Volver", icon=ft.Icons.ARROW_BACK, on_click=self.mostrar_empleado)

        self.page.add(
            ft.Column(
                [
                    ft.Text("Alta de Empleado", size=24, weight="bold"),
                    self.legajo,
                    self.dni,
                    self.apellido,
                    self.nombre,
                    self.direccion,
                    self.telefono,
                    ft.Row([guardar_btn, volver_btn], spacing=10),
                ],
                spacing=10,
            )
        )
        self.page.update()

    def guardar_empleado(self, e):
        try:
            self.cursor.execute(
                "INSERT INTO persona (dni, apellido, nombre, direccion, tele_contac) VALUES (%s, %s, %s, %s, %s)",
                (
                    self.dni.value,
                    self.apellido.value,
                    self.nombre.value,
                    self.direccion.value,
                    self.telefono.value,
                ),
            )
            self.cursor.execute(
                "INSERT INTO empleado (legajo, dni) VALUES (%s, %s)",
                (self.legajo.value, self.dni.value),
            )
            self.connection.commit()
            self.page.snack_bar = ft.SnackBar(ft.Text("Empleado guardado correctamente"))
            self.page.snack_bar.open = True
            self.mostrar_empleado()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al guardar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def consulta_empleado(self, e):
        self.page.clean()
        self.page.add(ft.Text("Consulta de Empleados", size=24, weight="bold"))
        self.page.add(self.create_empleado_table())
        self.page.add(ft.ElevatedButton("Volver", on_click=self.mostrar_empleado))
        self.page.update()

    def imprimir_empleados(self, e):
        self.page.snack_bar = ft.SnackBar(ft.Text("Función de impresión no implementada"))
        self.page.snack_bar.open = True
        self.page.update()

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback(self.page)

    def create_empleado_table(self):
        if not self.cursor:
            print("No hay conexión a la base de datos")
            return ft.Text("No hay conexión a la base de datos")

        listado_todos_empleados = """
            SELECT per.apellido, per.nombre, per.dni, per.direccion, per.tele_contac, emp.legajo
            FROM persona per INNER JOIN empleado emp ON per.dni = emp.dni
            ORDER BY per.apellido
        """
        self.cursor.execute(listado_todos_empleados)
        datos_empleados = self.cursor.fetchall()
        self.all_data = datos_empleados
        rows = self.get_rows(datos_empleados)

        data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Apellido")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("DNI")),
                ft.DataColumn(ft.Text("Dirección")),
                ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("Legajo")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=rows,
        )
        return data_table

    def get_rows(self, empleados):
        rows = []
        for empleado in empleados:
            eliminar_button = ft.IconButton(
                icon=ft.Icons.DELETE,
                tooltip="Borrar",
                on_click=lambda e, emp=empleado: self.eliminar_empleado(e, emp),
            )
            actualizar_button = ft.IconButton(
                icon=ft.Icons.EDIT,
                tooltip="Modificar",
                on_click=lambda e, emp=empleado: self.actualizar_empleado(e, emp),
            )
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(empleado[0])),
                        ft.DataCell(ft.Text(empleado[1])),
                        ft.DataCell(ft.Text(str(empleado[2]))),
                        ft.DataCell(ft.Text(empleado[3])),
                        ft.DataCell(ft.Text(empleado[4])),
                        ft.DataCell(ft.Text(str(empleado[5]))),
                        ft.DataCell(ft.Row(controls=[eliminar_button, actualizar_button])),
                    ],
                ),
            )
        return rows

    def search(self, e):
        search_term = self.search_field.value.lower()
        search_column = self.search_column.value
        filtered_data = []

        for row in self.all_data:
            if search_column == "legajo" and str(row[5]).lower().__contains__(search_term):
                filtered_data.append(row)
            elif search_column == "apellido" and row[0].lower().__contains__(search_term):
                filtered_data.append(row)
            elif search_column == "nombre" and row[1].lower().__contains__(search_term):
                filtered_data.append(row)
            elif search_column == "dni" and str(row[2]).lower().__contains__(search_term):
                filtered_data.append(row)
            elif search_column == "direccion" and row[3].lower().__contains__(search_term):
                filtered_data.append(row)
            elif search_column == "telefono" and row[4].lower().__contains__(search_term):
                filtered_data.append(row)

        self.data_table.rows = self.get_rows(filtered_data)
        self.page.update()

    def eliminar_empleado(self, e, empleado):
        try:
            dni = empleado[2]
            legajo = empleado[5]
            self.cursor.execute("DELETE FROM empleado WHERE legajo = %s", (legajo,))
            self.cursor.execute("DELETE FROM persona WHERE dni = %s", (dni,))
            self.connection.commit()
            self.page.snack_bar = ft.SnackBar(ft.Text("Empleado eliminado correctamente"))
            self.page.snack_bar.open = True
            self.mostrar_empleado()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def actualizar_empleado(self, e, empleado):
        self.page.clean()
        self.legajo = ft.TextField(label="Legajo", value=str(empleado[5]), width=300, disabled=True)
        self.dni = ft.TextField(label="DNI", value=str(empleado[2]), width=300, disabled=True)
        self.apellido = ft.TextField(label="Apellido", value=empleado[0], width=300)
        self.nombre = ft.TextField(label="Nombre", value=empleado[1], width=300)
        self.direccion = ft.TextField(label="Dirección", value=empleado[3], width=300)
        self.telefono = ft.TextField(label="Teléfono", value=empleado[4], width=300)

        guardar_btn = ft.ElevatedButton("Guardar Cambios", icon=ft.Icons.SAVE, on_click=lambda e: self.guardar_cambios_empleado(e, empleado))
        volver_btn = ft.ElevatedButton("Volver", icon=ft.Icons.ARROW_BACK, on_click=self.mostrar_empleado)

        self.page.add(
            ft.Column(
                [
                    ft.Text("Editar Empleado", size=24, weight="bold"),
                    self.legajo,
                    self.dni,
                    self.apellido,
                    self.nombre,
                    self.direccion,
                    self.telefono,
                    ft.Row([guardar_btn, volver_btn], spacing=10),
                ],
                spacing=10,
            )
        )
        self.page.update()

    def guardar_cambios_empleado(self, e, empleado):
        try:
            self.cursor.execute(
                "UPDATE persona SET apellido=%s, nombre=%s, direccion=%s, tele_contac=%s WHERE dni=%s",
                (
                    self.apellido.value,
                    self.nombre.value,
                    self.direccion.value,
                    self.telefono.value,
                    self.dni.value,
                ),
            )
            self.connection.commit()
            self.page.snack_bar = ft.SnackBar(ft.Text("Empleado actualizado correctamente"))
            self.page.snack_bar.open = True
            self.mostrar_empleado()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al actualizar: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()'''