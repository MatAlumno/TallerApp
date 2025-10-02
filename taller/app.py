import flet as ft

# Importar todas las herramientas desde la carpeta template
from template.Cliente import Herramienta_Cliente
from template.Empleado import Herramienta_Empleado
from template.Proveedor import Herramienta_Proveedor
from template.Repuesto import Herramienta_Repuesto
from template.Vehiculo import Herramienta_Vehiculo


def main(page: ft.Page):
    page.title = "Taller Mecánico"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = "adaptive"

    # Menú principal
    def mostrar_menu(page):
        page.clean()
        page.add(
            ft.Text("Sistema de Gestión - Taller Mecánico", size=25, weight="bold"),
            ft.Row(
                [
                    ft.ElevatedButton("Cliente", on_click=lambda e: Herramienta_Cliente(page, mostrar_menu)),
                    ft.ElevatedButton("Empleado", on_click=lambda e: Herramienta_Empleado(page, mostrar_menu)),
                    ft.ElevatedButton("Proveedor", on_click=lambda e: Herramienta_Proveedor(page, mostrar_menu)),
                    ft.ElevatedButton("Repuesto", on_click=lambda e: Herramienta_Repuesto(page, mostrar_menu)),
                    ft.ElevatedButton("Vehículo", on_click=lambda e: Herramienta_Vehiculo(page, mostrar_menu)),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                wrap=True
            )
        )
        page.update()

    mostrar_menu(page)



if __name__ == "__main__":
    ft.app(target=main)
