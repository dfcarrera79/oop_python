"""Vista de administración de clientes."""

from collections.abc import Callable

import flet as ft
from pydantic import ValidationError

from proformas.aplicacion import AplicacionProformas
from proformas.dominio import Cliente, TipoCliente
from proformas.ui.componentes import mensaje_error, mostrar_error


class VistaClientes:
    def __init__(
        self, page: ft.Page, aplicacion: AplicacionProformas, refrescar: Callable[[], None]
    ) -> None:
        self.page = page
        self.aplicacion = aplicacion
        self.refrescar = refrescar
        self.tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Identificación")),
                ft.DataColumn(ft.Text("Cliente")),
                ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("Email")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[],
        )

    def construir(self) -> list[ft.Control]:
        self.tabla.rows = [self._fila(cliente) for cliente in self.aplicacion.listar_clientes()]
        return [
            ft.Row(
                [
                    ft.FilledButton(
                        "Nuevo cliente",
                        icon=ft.Icons.ADD,
                        on_click=lambda _: self.abrir_formulario(),
                    )
                ]
            ),
            ft.Row([self.tabla], scroll=ft.ScrollMode.AUTO),
        ]

    def _fila(self, cliente: Cliente) -> ft.DataRow:
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(cliente.identificacion))),
                ft.DataCell(ft.Text(cliente.nombre)),
                ft.DataCell(ft.Text(cliente.telefono)),
                ft.DataCell(ft.Text(str(cliente.email))),
                ft.DataCell(
                    ft.Row(
                        [
                            ft.IconButton(
                                ft.Icons.EDIT_OUTLINED,
                                tooltip="Editar cliente",
                                on_click=lambda _: self.abrir_formulario(cliente=cliente),
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE_OUTLINE,
                                tooltip="Eliminar cliente",
                                on_click=lambda _: self._confirmar_eliminacion(cliente),
                            ),
                        ],
                        spacing=0,
                    )
                ),
            ]
        )

    def abrir_formulario(
        self,
        cliente: Cliente | None = None,
        identificacion: str = "",
        al_guardar: Callable[[Cliente], None] | None = None,
    ) -> None:
        campos = {
            "identificacion": ft.TextField(
                label="Cédula o RUC",
                value=str(cliente.identificacion) if cliente else identificacion,
                disabled=cliente is not None,
            ),
            "nombre": ft.TextField(
                label="Nombre o razón social", value=cliente.nombre if cliente else ""
            ),
            "direccion": ft.TextField(
                label="Dirección", value=cliente.direccion if cliente else ""
            ),
            "telefono": ft.TextField(label="Teléfono", value=cliente.telefono if cliente else ""),
            "email": ft.TextField(label="Email", value=str(cliente.email) if cliente else ""),
            "tipo": ft.Dropdown(
                label="Tipo",
                value=cliente.tipo.value if cliente else TipoCliente.PUBLICO.value,
                options=[
                    ft.DropdownOption(key=tipo.value, text=tipo.value.title())
                    for tipo in TipoCliente
                ],
            ),
        }
        self.page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Editar cliente" if cliente else "Nuevo cliente"),
                content=ft.Column(list(campos.values()), tight=True, scroll=ft.ScrollMode.AUTO),
                actions=[
                    ft.OutlinedButton("Cancelar", on_click=lambda _: self.page.pop_dialog()),
                    ft.FilledButton(
                        "Guardar",
                        on_click=lambda _: self._guardar(campos, cliente, al_guardar),
                    ),
                ],
            )
        )

    def _guardar(
        self,
        campos: dict[str, ft.Control],
        cliente_original: Cliente | None = None,
        al_guardar: Callable[[Cliente], None] | None = None,
    ) -> None:
        try:
            cliente = Cliente(
                identificacion=campos["identificacion"].value,
                nombre=campos["nombre"].value,
                direccion=campos["direccion"].value,
                telefono=campos["telefono"].value,
                email=campos["email"].value,
                tipo=campos["tipo"].value,
            )
            if cliente_original:
                self.aplicacion.actualizar_cliente(cliente)
            else:
                self.aplicacion.registrar_cliente(cliente)
        except (ValidationError, ValueError) as error:
            mostrar_error(self.page, mensaje_error(error))
            return
        self.page.pop_dialog()
        if al_guardar:
            al_guardar(cliente)
        else:
            self.refrescar()

    def _confirmar_eliminacion(self, cliente: Cliente) -> None:
        self.page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Eliminar cliente"),
                content=ft.Text(f"¿Deseas eliminar {cliente.nombre}?"),
                actions=[
                    ft.OutlinedButton("Cancelar", on_click=lambda _: self.page.pop_dialog()),
                    ft.FilledButton(
                        "Eliminar",
                        icon=ft.Icons.DELETE_OUTLINE,
                        on_click=lambda _: self._eliminar(str(cliente.identificacion)),
                    ),
                ],
            )
        )

    def _eliminar(self, identificacion: str) -> None:
        try:
            self.aplicacion.eliminar_cliente(identificacion)
        except (LookupError, ValueError) as error:
            self.page.pop_dialog()
            mostrar_error(self.page, str(error))
            return
        self.page.pop_dialog()
        self.refrescar()
