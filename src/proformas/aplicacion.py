"""Casos de aplicación coordinados sobre SQLite."""

import os
from pathlib import Path

from proformas.dominio import RUC, Cliente, CuentaPago, Estado, ItemProforma, Producto, Proforma
from proformas.exportacion import ExportadorProformaPDF
from proformas.persistencia.cuentas_pago import RepositorioCuentasPagoSQLite
from proformas.persistencia.proformas import RepositorioProformasSQLite
from proformas.persistencia.sqlite import (
    CatalogoProductosSQLite,
    RegistroClientesSQLite,
)


class AplicacionProformas:
    """API de la interfaz: evita que Flet conozca SQL o detalles de PDF."""

    def __init__(
        self,
        ruta_bd: str | Path | None = None,
    ) -> None:
        ruta_bd = ruta_bd or ruta_base_datos()
        self._productos = CatalogoProductosSQLite(ruta_bd)
        self._clientes = RegistroClientesSQLite(ruta_bd)
        self._proformas = RepositorioProformasSQLite(ruta_bd)
        self._cuentas_pago = RepositorioCuentasPagoSQLite(ruta_bd)
        self._exportador = ExportadorProformaPDF()

    def registrar_producto(self, producto: Producto) -> None:
        self._productos.registrar(producto)

    def actualizar_producto(self, producto: Producto) -> None:
        self._productos.actualizar(producto)

    def registrar_cliente(self, cliente: Cliente) -> None:
        self._clientes.registrar(cliente)

    def actualizar_cliente(self, cliente: Cliente) -> None:
        self._clientes.actualizar(cliente)

    def buscar_cliente(self, identificacion: RUC | str) -> Cliente | None:
        return self._clientes.buscar(identificacion)

    def buscar_clientes(self, termino: str) -> list[Cliente]:
        return self._clientes.buscar_coincidencias(termino)

    def buscar_producto(self, codigo: str) -> Producto | None:
        return self._productos.buscar(codigo)

    def listar_productos(self) -> list[Producto]:
        return self._productos.listar()

    def listar_clientes(self) -> list[Cliente]:
        return self._clientes.listar()

    def eliminar_producto(self, codigo: str) -> None:
        self._productos.eliminar(codigo)

    def eliminar_cliente(self, identificacion: RUC | str) -> None:
        self._clientes.eliminar(identificacion)

    def guardar_cuenta_pago(self, cuenta: CuentaPago) -> CuentaPago:
        return self._cuentas_pago.registrar(cuenta)

    def listar_cuentas_pago(self) -> list[CuentaPago]:
        return self._cuentas_pago.listar()

    def eliminar_cuenta_pago(self, cuenta_id: int) -> None:
        self._cuentas_pago.eliminar(cuenta_id)

    def crear_proforma(
        self,
        cliente: Cliente,
        items: list[ItemProforma],
        observaciones: str = "",
        instrucciones_pago: str = "",
    ) -> Proforma:
        if cliente.estado != Estado.ACTIVO:
            raise ValueError("El cliente debe estar activo")
        if not items:
            raise ValueError("Agrega al menos un producto a la proforma")
        return Proforma(
            numero=self._proformas.siguiente_numero(),
            cliente=cliente,
            items=items,
            observaciones=observaciones,
            instrucciones_pago=instrucciones_pago,
        )

    def guardar_proforma(self, proforma: Proforma) -> None:
        self._proformas.guardar(proforma)

    def buscar_proforma(self, numero: str) -> Proforma | None:
        return self._proformas.buscar(numero)

    def listar_proformas(self) -> list[Proforma]:
        return self._proformas.listar()

    def eliminar_proforma(self, numero: str) -> None:
        self._proformas.eliminar(numero)

    def exportar_proforma_pdf(self, numero: str, destino: str | Path | None = None) -> Path:
        proforma = self.buscar_proforma(numero)
        if proforma is None:
            raise LookupError(f"No existe la proforma {numero}")
        ruta = Path(destino) if destino else Path("output/pdf") / f"{numero}.pdf"
        return self._exportador.exportar(proforma, ruta)


def ruta_base_datos() -> Path:
    """Ubica SQLite en el almacenamiento persistente de Flet al desplegar."""
    almacenamiento_flet = os.getenv("FLET_APP_STORAGE_DATA")
    if almacenamiento_flet:
        return Path(almacenamiento_flet) / "proformas.db"
    return Path("data/proformas.db")
