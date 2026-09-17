"""Vista de creación y administración de proformas."""

from collections.abc import Callable
from pathlib import Path

import flet as ft
from pydantic import ValidationError

from proformas.aplicacion import AplicacionProformas
from proformas.dominio import Cliente, CuentaPago, ItemProforma, Producto, Talla
from proformas.ui.componentes import mensaje_error, mostrar_error, seccion, total


class VistaProformas:
    def __init__(
        self,
        page: ft.Page,
        aplicacion: AplicacionProformas,
        refrescar: Callable[[], None],
        nuevo_cliente: Callable[..., None] | None = None,
        nuevo_producto: Callable[..., None] | None = None,
    ) -> None:
        self.page = page
        self.aplicacion = aplicacion
        self.refrescar = refrescar
        self.nuevo_cliente = nuevo_cliente
        self.nuevo_producto = nuevo_producto
        self.cliente: Cliente | None = None
        self.items: list[ItemProforma] = []
        self.identificacion = ft.TextField(
            label="Cédula o RUC", width=260, on_submit=self._buscar_cliente
        )
        self.resultado_cliente = ft.Column(
            [ft.Text("Busca un cliente para comenzar", color=ft.Colors.GREY_600)], spacing=2
        )
        self.producto = ft.Dropdown(
            label="Producto", width=520, enable_filter=True, enable_search=True
        )
        self.cantidad = ft.TextField(label="Cantidad", value="1", width=110)
        self.talla = ft.Dropdown(
            label="Talla",
            width=125,
            options=[
                ft.DropdownOption(key="", text="Sin talla"),
                *[ft.DropdownOption(key=talla.value, text=talla.value) for talla in Talla],
            ],
        )
        self.tabla_items = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Cant.")),
                ft.DataColumn(ft.Text("Código")),
                ft.DataColumn(ft.Text("Producto")),
                ft.DataColumn(ft.Text("Precio"), numeric=True),
                ft.DataColumn(ft.Text("Total"), numeric=True),
                ft.DataColumn(ft.Text("")),
            ],
            rows=[],
        )
        self.area_items = ft.Container()
        self.observaciones = ft.TextField(label="Observaciones", multiline=True, min_lines=2)
        self.instrucciones_pago = ft.TextField(
            label="Instrucciones de pago",
            multiline=True,
            min_lines=2,
        )
        self.cuenta_pago = ft.Dropdown(
            label="Cuenta de pago guardada",
            expand=True,
            on_select=self._cargar_cuenta_pago,
        )
        self.resumen = ft.Column()

    def construir(self) -> list[ft.Control]:
        self._cargar_productos()
        self._cargar_cuentas_pago()
        self._actualizar_items()
        return [
            seccion(
                "1. Cliente",
                ft.Column(
                    [
                        ft.Row(
                            [
                                self.identificacion,
                                ft.FilledButton(
                                    "Buscar", icon=ft.Icons.SEARCH, on_click=self._buscar_cliente
                                ),
                                ft.OutlinedButton(
                                    "Nuevo cliente",
                                    icon=ft.Icons.PERSON_ADD,
                                    on_click=self._nuevo_cliente,
                                ),
                            ],
                            wrap=True,
                        ),
                        self.resultado_cliente,
                    ]
                ),
            ),
            seccion(
                "2. Productos",
                ft.Column(
                    [
                        ft.Row(
                            [
                                self.producto,
                                self.cantidad,
                                self.talla,
                                ft.FilledButton(
                                    "Agregar", icon=ft.Icons.ADD, on_click=self._agregar_item
                                ),
                                ft.OutlinedButton(
                                    "Nuevo producto",
                                    icon=ft.Icons.ADD_BOX_OUTLINED,
                                    on_click=self._nuevo_producto,
                                ),
                            ],
                            wrap=True,
                        ),
                        self.area_items,
                    ]
                ),
            ),
            ft.ResponsiveRow(
                [
                    ft.Container(
                        seccion(
                            "3. Detalles finales",
                            ft.Column(
                                [
                                    self.observaciones,
                                    ft.Row(
                                        [
                                            self.cuenta_pago,
                                            ft.IconButton(
                                                ft.Icons.SAVE_OUTLINED,
                                                tooltip="Guardar estas instrucciones",
                                                on_click=self._guardar_cuenta_pago,
                                            ),
                                            ft.IconButton(
                                                ft.Icons.DELETE_OUTLINE,
                                                tooltip="Eliminar cuenta seleccionada",
                                                on_click=self._eliminar_cuenta_pago,
                                            ),
                                        ]
                                    ),
                                    self.instrucciones_pago,
                                ]
                            ),
                        ),
                        col={"sm": 12, "lg": 8},
                    ),
                    ft.Container(
                        seccion(
                            "Resumen",
                            ft.Column(
                                [
                                    self.resumen,
                                    ft.FilledButton(
                                        "Guardar y exportar PDF",
                                        icon=ft.Icons.PICTURE_AS_PDF,
                                        on_click=self._guardar_y_exportar,
                                    ),
                                ]
                            ),
                        ),
                        col={"sm": 12, "lg": 4},
                    ),
                ]
            ),
            seccion("Proformas guardadas", self._tabla_proformas()),
        ]

    def _tabla_proformas(self) -> ft.Row:
        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Número")),
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("Cliente")),
                ft.DataColumn(ft.Text("Total"), numeric=True),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(proforma.numero)),
                        ft.DataCell(ft.Text(f"{proforma.fecha:%d/%m/%Y}")),
                        ft.DataCell(ft.Text(proforma.cliente.nombre)),
                        ft.DataCell(ft.Text(f"${proforma.total():,.2f}")),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        ft.Icons.PICTURE_AS_PDF,
                                        tooltip="Exportar nuevamente",
                                        on_click=self._exportar_existente(proforma.numero),
                                    ),
                                    ft.IconButton(
                                        ft.Icons.DELETE_OUTLINE,
                                        tooltip="Eliminar proforma",
                                        on_click=lambda _, numero=proforma.numero: (
                                            self._confirmar_eliminacion(numero)
                                        ),
                                    ),
                                ],
                                spacing=0,
                            )
                        ),
                    ]
                )
                for proforma in self.aplicacion.listar_proformas()
            ],
        )
        return ft.Row([tabla], scroll=ft.ScrollMode.AUTO)

    def _buscar_cliente(self, _: object) -> None:
        termino = (self.identificacion.value or "").strip()
        if not termino:
            mostrar_error(self.page, "Escribe parte de la identificación o del nombre")
            return
        coincidencias = self.aplicacion.buscar_clientes(termino)
        if not coincidencias:
            mostrar_error(self.page, "No se encontraron clientes. Puedes crear uno nuevo.")
            return
        if len(coincidencias) == 1:
            self._seleccionar_cliente(coincidencias[0])
        else:
            self._mostrar_coincidencias(coincidencias)
        self.page.update()

    def _mostrar_coincidencias(self, clientes: list[Cliente]) -> None:
        self.page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Selecciona un cliente"),
                content=ft.Column(
                    [
                        ft.ListTile(
                            title=ft.Text(cliente.nombre),
                            subtitle=ft.Text(
                                f"{cliente.identificacion} · {cliente.direccion or 'Sin dirección'}"
                            ),
                            on_click=lambda _, item=cliente: self._elegir_coincidencia(item),
                        )
                        for cliente in clientes
                    ],
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                actions=[ft.OutlinedButton("Cancelar", on_click=lambda _: self.page.pop_dialog())],
            )
        )

    def _elegir_coincidencia(self, cliente: Cliente) -> None:
        self.page.pop_dialog()
        self._seleccionar_cliente(cliente)
        self.page.update()

    def _seleccionar_cliente(self, cliente: Cliente, creado: bool = False) -> None:
        self.cliente = cliente
        self.identificacion.value = str(cliente.identificacion)
        self.resultado_cliente.controls = [
            ft.Text(
                f"✓ {cliente.nombre}{' · cliente creado' if creado else ''}",
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.GREEN_700,
            ),
            ft.Text(f"Identificación: {cliente.identificacion}"),
            ft.Text(f"Dirección: {cliente.direccion or '-'}"),
            ft.Text(f"Teléfono: {cliente.telefono or '-'} · Email: {cliente.email or '-'}"),
            ft.Text(f"Tipo: {cliente.tipo.value.title()} · Estado: {cliente.estado.value.title()}"),
        ]

    def _nuevo_cliente(self, _: object) -> None:
        if self.nuevo_cliente:
            self.nuevo_cliente(
                identificacion=self.identificacion.value or "",
                al_guardar=self._cliente_creado,
            )

    def _cliente_creado(self, cliente: Cliente) -> None:
        self._seleccionar_cliente(cliente, creado=True)
        self.page.update()

    def _nuevo_producto(self, _: object) -> None:
        if self.nuevo_producto:
            self.nuevo_producto(al_guardar=self._producto_creado)

    def _producto_creado(self, producto: Producto) -> None:
        self._cargar_productos()
        self.producto.value = producto.codigo
        self.page.update()

    def _cargar_productos(self) -> None:
        self.producto.options = [
            ft.DropdownOption(key=item.codigo, text=f"{item.codigo} - {item.nombre}")
            for item in self.aplicacion.listar_productos()
        ]

    def _cargar_cuentas_pago(self) -> None:
        self.cuenta_pago.options = [
            ft.DropdownOption(key=str(cuenta.id), text=cuenta.nombre)
            for cuenta in self.aplicacion.listar_cuentas_pago()
        ]

    def _cargar_cuenta_pago(self, _: object) -> None:
        cuenta = next(
            (
                item
                for item in self.aplicacion.listar_cuentas_pago()
                if str(item.id) == self.cuenta_pago.value
            ),
            None,
        )
        if cuenta:
            self.instrucciones_pago.value = cuenta.instrucciones
            self.page.update()

    def _guardar_cuenta_pago(self, _: object) -> None:
        nombre = ft.TextField(label="Nombre para identificar la cuenta")
        self.page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Guardar cuenta de pago"),
                content=nombre,
                actions=[
                    ft.OutlinedButton("Cancelar", on_click=lambda _: self.page.pop_dialog()),
                    ft.FilledButton(
                        "Guardar",
                        on_click=lambda _: self._confirmar_cuenta_pago(nombre.value or ""),
                    ),
                ],
            )
        )

    def _confirmar_cuenta_pago(self, nombre: str) -> None:
        try:
            cuenta = self.aplicacion.guardar_cuenta_pago(
                CuentaPago(nombre=nombre, instrucciones=self.instrucciones_pago.value or "")
            )
        except (ValidationError, ValueError) as error:
            mostrar_error(self.page, mensaje_error(error))
            return
        self.page.pop_dialog()
        self._cargar_cuentas_pago()
        self.cuenta_pago.value = str(cuenta.id)
        self.page.update()

    def _eliminar_cuenta_pago(self, _: object) -> None:
        if not self.cuenta_pago.value:
            mostrar_error(self.page, "Selecciona una cuenta guardada")
            return
        self.aplicacion.eliminar_cuenta_pago(int(self.cuenta_pago.value))
        self.cuenta_pago.value = None
        self.instrucciones_pago.value = ""
        self._cargar_cuentas_pago()
        self.page.update()

    def _agregar_item(self, _: object) -> None:
        producto = self.aplicacion.buscar_producto(self.producto.value or "")
        if producto is None:
            mostrar_error(self.page, "Selecciona un producto existente")
            return
        try:
            item = ItemProforma(
                producto=producto,
                cantidad=int(self.cantidad.value),
                tipo_cliente=self.cliente.tipo if self.cliente else None,
                talla=Talla(self.talla.value) if self.talla.value else None,
            )
        except (ValueError, ValidationError) as error:
            mostrar_error(self.page, mensaje_error(error))
            return
        self.items.append(item)
        self._actualizar_items()
        self.page.update()

    def _actualizar_items(self) -> None:
        self.tabla_items.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(item.cantidad))),
                    ft.DataCell(ft.Text(item.producto.codigo)),
                    ft.DataCell(ft.Text(item.producto.nombre)),
                    ft.DataCell(ft.Text(f"${float(item.producto.precio):,.2f}")),
                    ft.DataCell(ft.Text(f"${item.total():,.2f}")),
                    ft.DataCell(
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE,
                            tooltip="Quitar",
                            on_click=self._eliminar_item(indice),
                        )
                    ),
                ]
            )
            for indice, item in enumerate(self.items)
        ]
        subtotal = sum(item.subtotal() for item in self.items)
        iva = sum(item.impuesto() for item in self.items)
        self.resumen.controls = [
            total("Subtotal", subtotal),
            total("IVA", iva),
            ft.Divider(),
            total("Total", subtotal + iva, destacado=True),
        ]
        self.area_items.content = (
            ft.Row([self.tabla_items], scroll=ft.ScrollMode.AUTO)
            if self.items
            else ft.Container(
                ft.Text(
                    "Todavía no has agregado productos.",
                    color=ft.Colors.GREY_600,
                    italic=True,
                ),
                padding=12,
            )
        )

    def _eliminar_item(self, indice: int) -> Callable[[object], None]:
        def eliminar(_: object) -> None:
            self.items.pop(indice)
            self._actualizar_items()
            self.page.update()

        return eliminar

    def _guardar_y_exportar(self, _: object) -> None:
        if self.cliente is None:
            mostrar_error(self.page, "Busca o crea un cliente antes de guardar")
            return
        try:
            proforma = self.aplicacion.crear_proforma(
                self.cliente,
                self.items,
                self.observaciones.value,
                self.instrucciones_pago.value,
            )
            self.aplicacion.guardar_proforma(proforma)
            ruta = self.aplicacion.exportar_proforma_pdf(proforma.numero)
        except (ValueError, LookupError) as error:
            mostrar_error(self.page, str(error))
            return
        self._mostrar_pdf(ruta, f"Proforma {proforma.numero} guardada")
        self.items.clear()
        self._actualizar_items()

    def _exportar_existente(self, numero: str) -> Callable[[object], None]:
        def exportar(_: object) -> None:
            try:
                ruta = self.aplicacion.exportar_proforma_pdf(numero)
            except LookupError as error:
                mostrar_error(self.page, str(error))
                return
            self._mostrar_pdf(ruta, "PDF exportado")

        return exportar

    def _mostrar_pdf(self, ruta: Path, titulo: str) -> None:
        uri = ruta.resolve().as_uri()
        self.page.launch_url(uri)
        self.page.show_dialog(
            ft.AlertDialog(
                title=ft.Text(titulo),
                content=ft.Text(str(ruta.resolve()), selectable=True),
                actions=[
                    ft.OutlinedButton("Abrir PDF", on_click=lambda _: self.page.launch_url(uri)),
                    ft.FilledButton("Aceptar", on_click=lambda _: self.page.pop_dialog()),
                ],
            )
        )

    def _confirmar_eliminacion(self, numero: str) -> None:
        self.page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Eliminar proforma"),
                content=ft.Text(f"¿Deseas eliminar definitivamente {numero}?"),
                actions=[
                    ft.OutlinedButton("Cancelar", on_click=lambda _: self.page.pop_dialog()),
                    ft.FilledButton(
                        "Eliminar",
                        icon=ft.Icons.DELETE_OUTLINE,
                        on_click=lambda _: self._eliminar(numero),
                    ),
                ],
            )
        )

    def _eliminar(self, numero: str) -> None:
        try:
            self.aplicacion.eliminar_proforma(numero)
        except LookupError as error:
            self.page.pop_dialog()
            mostrar_error(self.page, str(error))
            return
        self.page.pop_dialog()
        self.refrescar()
