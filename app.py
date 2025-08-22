import flet as ft
from templates.cliente import Pagina_Cliente
from templates.empleado import Pagina_Empleado
from templates.ficha_tecnica import Pagina_FichaTecnica
from templates.presupuesto import Pagina_Presupuesto
from templates.proveedor import Pagina_Proveedor
from templates.repuesto import Pagina_Repuesto


def main_menu(page: ft.Page):
    page.clean()
    page.title = "Taller Mecánico"

    opciones = [
        ("Clientes", Pagina_Cliente),
        ("Empleados", Pagina_Empleado),
        ("Fichas Técnicas", Pagina_FichaTecnica),
        ("Presupuestos", Pagina_Presupuesto),
        ("Proveedores", Pagina_Proveedor),
        ("Repuestos", Pagina_Repuesto)
    ]

    botones = []
    for nombre, clase in opciones:
        botones.append(ft.ElevatedButton(
            nombre, 
            on_click=lambda e, c=clase: c(page, main_menu)
        ))

    page.add(
        ft.Column(
            controls=[ft.Text("Menú Principal", size=25, weight="bold")] + botones,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )
    )

def main(page: ft.Page):
    main_menu(page)

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)

'''import flet as ft
import mysql.connector

# Conexión única
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

# Módulo Clientes
class Pagina_Cliente:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None
        self.mostrar_cliente()

    def mostrar_cliente(self):
        self.page.clean()
        header = ft.Row(
            controls=[
                ft.Text("Gestión de Clientes", size=20, weight="bold"),
                ft.ElevatedButton(text="Alta"),
                ft.ElevatedButton(text="Consulta"),
                ft.ElevatedButton(text="Imprimir"),
                ft.ElevatedButton(text="<-- Volver al Menú", on_click=self.volver_al_menu),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        data_table = self.create_client_table()
        self.page.add(
            ft.Column(
                controls=[header, data_table],
                spacing=20,
                expand=True
            )
        )

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback(self.page)

    def create_client_table(self):
        if not self.cursor:
            return ft.Text("No hay conexión a la base de datos")

        self.cursor.execute("""
            SELECT per.apellido, per.nombre, per.dni,
                   per.direccion, per.tele_contac, c.cod_cliente
            FROM persona per INNER JOIN cliente c ON per.dni = c.dni
            ORDER BY per.apellido
        """)
        datos_clientes = self.cursor.fetchall()
        rows = []
        for cliente in datos_clientes:
            eliminar_btn = ft.IconButton(icon=ft.icons.DELETE, tooltip="Eliminar",
                                        on_click=lambda e, c=cliente: self.eliminar_cliente(e, c))
            editar_btn = ft.IconButton(icon=ft.icons.EDIT, tooltip="Editar",
                                      on_click=lambda e, c=cliente: self.actualizar_cliente(e, c))
            rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(cliente[0])),
                    ft.DataCell(ft.Text(cliente[1])),
                    ft.DataCell(ft.Text(str(cliente[2]))),
                    ft.DataCell(ft.Text(cliente[3])),
                    ft.DataCell(ft.Text(cliente[4])),
                    ft.DataCell(ft.Text(str(cliente[5]))),
                    ft.DataCell(ft.Row(controls=[eliminar_btn, editar_btn]))
                ])
            )
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Apellido")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("DNI")),
                ft.DataColumn(ft.Text("Dirección")),
                ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("Código Cliente")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=rows,
            column_spacing=10,
            data_row_height=40,
            heading_row_height=45,
            border=ft.border.all(1, ft.colors.BLUE_200)
        )

    def eliminar_cliente(self, e, cliente):
        print(f"Eliminar cliente {cliente}")

    def actualizar_cliente(self, e, cliente):
        print(f"Actualizar cliente {cliente}")

# Módulo Usuarios
class Pagina_Usuario:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None
        self.mostrar_usuario()

    def mostrar_usuario(self):
        self.page.clean()
        header = ft.Row(
            controls=[
                ft.Text("Gestión de Usuarios", size=20, weight="bold"),
                ft.ElevatedButton(text="Alta"),
                ft.ElevatedButton(text="Consulta"),
                ft.ElevatedButton(text="Imprimir"),
                ft.ElevatedButton(text="<-- Volver al Menú", on_click=self.volver_al_menu),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        data_table = self.create_user_table()
        self.page.add(
            ft.Column(
                controls=[header, data_table],
                spacing=20,
                expand=True
            )
        )

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback(self.page)

    def create_user_table(self):
        if not self.cursor:
            return ft.Text("No hay conexión a la base de datos")

        self.cursor.execute("""
            SELECT id_usuario, username, rol, estado
            FROM usuario
            ORDER BY username
        """)
        datos_usuarios = self.cursor.fetchall()
        rows = []
        for usuario in datos_usuarios:
            eliminar_btn = ft.IconButton(icon=ft.icons.DELETE, tooltip="Eliminar",
                                        on_click=lambda e, u=usuario: self.eliminar_usuario(e, u))
            editar_btn = ft.IconButton(icon=ft.icons.EDIT, tooltip="Editar",
                                      on_click=lambda e, u=usuario: self.actualizar_usuario(e, u))
            rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(usuario[0]))),
                    ft.DataCell(ft.Text(usuario[1])),
                    ft.DataCell(ft.Text(usuario[2])),
                    ft.DataCell(ft.Text(usuario[3])),
                    ft.DataCell(ft.Row(controls=[eliminar_btn, editar_btn]))
                ])
            )
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID Usuario")),
                ft.DataColumn(ft.Text("Username")),
                ft.DataColumn(ft.Text("Rol")),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=rows,
            column_spacing=10,
            data_row_height=40,
            heading_row_height=45,
            border=ft.border.all(1, ft.colors.BLUE_200)
        )

    def eliminar_usuario(self, e, usuario):
        print(f"Eliminar usuario {usuario}")

    def actualizar_usuario(self, e, usuario):
        print(f"Actualizar usuario {usuario}")

# Menú principal
def main_menu(page: ft.Page):
    page.clean()
    page.title = "Taller Mecánico - Menú Principal"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 50
    page.add(
        ft.Column(
            controls=[
                ft.Text("Taller Mecánico", size=30, weight="bold"),
                ft.ElevatedButton("Gestión de Clientes", on_click=lambda e: Pagina_Cliente(page, main_menu)),
                ft.ElevatedButton("Gestión de Usuarios", on_click=lambda e: Pagina_Usuario(page, main_menu)),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

def main(page: ft.Page):
    main_menu(page)

if __name__ == "__main__":
    ft.app(main, view=ft.AppView.WEB_BROWSER)
    '''
