"""Composición y navegación principal de la interfaz Flet."""

import flet as ft

from proformas.aplicacion import AplicacionProformas
from proformas.ui.vista_clientes import VistaClientes
from proformas.ui.vista_productos import VistaProductos
from proformas.ui.vista_proformas import VistaProformas


class AplicacionFlet:
    def __init__(self, page: ft.Page, aplicacion: AplicacionProformas | None = None) -> None:
        self.page = page
        self.aplicacion = aplicacion or AplicacionProformas()
        self.titulo = ft.Text("Nueva proforma", size=24, weight=ft.FontWeight.W_600)
        self.contenido = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
        self.productos = VistaProductos(page, self.aplicacion, self.mostrar_productos)
        self.clientes = VistaClientes(page, self.aplicacion, self.mostrar_clientes)
        self.proformas = VistaProformas(
            page,
            self.aplicacion,
            self.mostrar_proformas,
            nuevo_cliente=self.clientes.abrir_formulario,
            nuevo_producto=self.productos.abrir_formulario,
        )

    def construir(self) -> None:
        self.page.title = "CM Insumos Médicos - Proformas"
        self.page.padding = 0
        self.page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE_800, use_material3=True)
        self.page.add(
            ft.Row(
                [
                    self._navegacion(),
                    ft.VerticalDivider(width=1),
                    ft.Container(
                        ft.Column([self.titulo, self.contenido], expand=True),
                        padding=24,
                        expand=True,
                    ),
                ],
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            )
        )
        self.mostrar_proformas()

    def _navegacion(self) -> ft.NavigationRail:
        return ft.NavigationRail(
            selected_index=0,
            extended=True,
            min_extended_width=210,
            leading=ft.Container(
                ft.Column(
                    [
                        ft.Text("CM", size=26, weight=ft.FontWeight.BOLD),
                        ft.Text("Insumos médicos", size=12),
                    ],
                    spacing=0,
                ),
                padding=20,
            ),
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.DESCRIPTION_OUTLINED,
                    selected_icon=ft.Icons.DESCRIPTION,
                    label="Proformas",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.INVENTORY_2_OUTLINED,
                    selected_icon=ft.Icons.INVENTORY_2,
                    label="Productos",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.PEOPLE_OUTLINE,
                    selected_icon=ft.Icons.PEOPLE,
                    label="Clientes",
                ),
            ],
            on_change=self._cambiar_vista,
        )

    def _cambiar_vista(self, evento: ft.Event[ft.NavigationRail]) -> None:
        indice = evento.control.selected_index or 0
        (self.mostrar_proformas, self.mostrar_productos, self.mostrar_clientes)[indice]()

    def mostrar_proformas(self) -> None:
        self._mostrar("Nueva proforma", self.proformas.construir())

    def mostrar_productos(self) -> None:
        self._mostrar("Productos", self.productos.construir())

    def mostrar_clientes(self) -> None:
        self._mostrar("Clientes", self.clientes.construir())

    def _mostrar(self, titulo: str, controles: list[ft.Control]) -> None:
        self.titulo.value = titulo
        self.contenido.controls = controles
        self.page.update()


def construir_interfaz(page: ft.Page) -> None:
    AplicacionFlet(page).construir()
