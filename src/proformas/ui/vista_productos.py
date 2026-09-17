"""Vista de administración de productos."""

from collections.abc import Callable

import flet as ft
from pydantic import ValidationError

from proformas.aplicacion import AplicacionProformas
from proformas.dominio import TASAS_IVA_DISPONIBLES, Producto, calcular_precio_sin_iva
from proformas.ui.componentes import mensaje_error, mostrar_error


class VistaProductos:
    def __init__(
        self, page: ft.Page, aplicacion: AplicacionProformas, refrescar: Callable[[], None]
    ) -> None:
        self.page = page
        self.aplicacion = aplicacion
        self.refrescar = refrescar
        self.tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Código")),
                ft.DataColumn(ft.Text("Producto")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[],
        )

    def construir(self) -> list[ft.Control]:
        self.tabla.rows = [self._fila(producto) for producto in self.aplicacion.listar_productos()]
        return [
            ft.Row(
                [
                    ft.FilledButton(
                        "Nuevo producto",
                        icon=ft.Icons.ADD,
                        on_click=lambda _: self.abrir_formulario(),
                    )
                ]
            ),
            ft.Row([self.tabla], scroll=ft.ScrollMode.AUTO),
        ]

    def _fila(self, producto: Producto) -> ft.DataRow:
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(producto.codigo)),
                ft.DataCell(ft.Text(producto.nombre)),
                ft.DataCell(ft.Text(f"${float(producto.precio):,.2f}")),
                ft.DataCell(
                    ft.Row(
                        [
                            ft.IconButton(
                                ft.Icons.EDIT_OUTLINED,
                                tooltip="Editar producto",
                                on_click=lambda _: self.abrir_formulario(producto),
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE_OUTLINE,
                                tooltip="Eliminar producto",
                                on_click=lambda _: self._confirmar_eliminacion(producto),
                            ),
                        ],
                        spacing=0,
                    )
                ),
            ]
        )

    def abrir_formulario(
        self,
        producto: Producto | None = None,
        al_guardar: Callable[[Producto], None] | None = None,
    ) -> None:
        precio = ft.TextField(
            label="Precio unitario", value=str(producto.precio) if producto else "0"
        )
        iva = ft.Dropdown(
            label="IVA",
            value=str(int(producto.iva_pct)) if producto else "15",
            options=[
                ft.DropdownOption(key=str(int(tasa)), text=f"{tasa:.0f}%")
                for tasa in TASAS_IVA_DISPONIBLES
            ],
        )
        incluye_iva = ft.Checkbox(label="El precio ingresado incluye IVA", value=False)
        precio_base = ft.Text("Precio sin IVA que se guardará: $0.00")
        campos = {
            "codigo": ft.TextField(
                label="Código",
                value=producto.codigo if producto else "",
                disabled=producto is not None,
            ),
            "nombre": ft.TextField(label="Nombre", value=producto.nombre if producto else ""),
            "descripcion": ft.TextField(
                label="Descripción", value=producto.descripcion if producto else ""
            ),
            "precio": precio,
            "iva": iva,
            "incluye_iva": incluye_iva,
            "precio_base": precio_base,
        }
        precio.on_change = lambda _: self._actualizar_precio_base(campos)
        iva.on_select = lambda _: self._actualizar_precio_base(campos)
        incluye_iva.on_change = lambda _: self._actualizar_precio_base(campos)
        self._actualizar_precio_base(campos, actualizar_pagina=False)
        self.page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Editar producto" if producto else "Nuevo producto"),
                content=ft.Column(list(campos.values()), tight=True),
                actions=[
                    ft.OutlinedButton("Cancelar", on_click=lambda _: self.page.pop_dialog()),
                    ft.FilledButton(
                        "Guardar",
                        on_click=lambda _: self._guardar(campos, producto, al_guardar),
                    ),
                ],
            )
        )

    def _actualizar_precio_base(
        self, campos: dict[str, ft.Control], *, actualizar_pagina: bool = True
    ) -> None:
        try:
            precio = calcular_precio_sin_iva(
                campos["precio"].value,
                float(campos["iva"].value),
                incluye_iva=bool(campos["incluye_iva"].value),
            )
            campos["precio_base"].value = f"Precio sin IVA que se guardará: ${precio}"
            campos["precio_base"].color = ft.Colors.GREY_700
        except (TypeError, ValueError):
            campos["precio_base"].value = "Ingresa un precio válido"
            campos["precio_base"].color = ft.Colors.RED_700
        if actualizar_pagina:
            self.page.update()

    def _guardar(
        self,
        campos: dict[str, ft.Control],
        producto_original: Producto | None = None,
        al_guardar: Callable[[Producto], None] | None = None,
    ) -> None:
        try:
            producto = Producto(
                codigo=campos["codigo"].value,
                nombre=campos["nombre"].value,
                descripcion=campos["descripcion"].value,
                precio=calcular_precio_sin_iva(
                    campos["precio"].value,
                    float(campos["iva"].value),
                    incluye_iva=bool(campos["incluye_iva"].value),
                ),
                iva_pct=campos["iva"].value,
            )
            if producto_original:
                self.aplicacion.actualizar_producto(producto)
            else:
                self.aplicacion.registrar_producto(producto)
        except (ValidationError, ValueError) as error:
            mostrar_error(self.page, mensaje_error(error))
            return
        self.page.pop_dialog()
        if al_guardar:
            al_guardar(producto)
        else:
            self.refrescar()

    def _confirmar_eliminacion(self, producto: Producto) -> None:
        self.page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Eliminar producto"),
                content=ft.Text(f"¿Deseas eliminar {producto.codigo} - {producto.nombre}?"),
                actions=[
                    ft.OutlinedButton("Cancelar", on_click=lambda _: self.page.pop_dialog()),
                    ft.FilledButton(
                        "Eliminar",
                        icon=ft.Icons.DELETE_OUTLINE,
                        on_click=lambda _: self._eliminar(producto.codigo),
                    ),
                ],
            )
        )

    def _eliminar(self, codigo: str) -> None:
        try:
            self.aplicacion.eliminar_producto(codigo)
        except (LookupError, ValueError) as error:
            self.page.pop_dialog()
            mostrar_error(self.page, str(error))
            return
        self.page.pop_dialog()
        self.refrescar()
