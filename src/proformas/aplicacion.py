"""Coordinación de la aplicación sobre catálogos SQLite."""

from pathlib import Path

from proformas.dominio import RUC, Cliente, Estado, ItemProforma, Producto, Proforma
from proformas.persistencia.sqlite import (
    CatalogoProductos,
    CatalogoProductosSQLite,
    RegistroClientes,
    RegistroClientesSQLite,
)


class AplicacionProformas:
    """Coordina operaciones sin conocer detalles de consola ni sentencias SQL."""

    def __init__(
        self,
        ruta_bd: str | Path = "data/proformas.db",
        catalogo_productos: CatalogoProductos | None = None,
        registro_clientes: RegistroClientes | None = None,
    ) -> None:
        self._productos = catalogo_productos or CatalogoProductosSQLite(ruta_bd)
        self._clientes = registro_clientes or RegistroClientesSQLite(ruta_bd)

    def registrar_producto(self, producto: Producto) -> None:
        self._productos.registrar(producto)

    def registrar_cliente(self, cliente: Cliente) -> None:
        self._clientes.registrar(cliente)

    def listar_productos(self) -> list[Producto]:
        return self._productos.listar()

    def listar_clientes(self) -> list[Cliente]:
        return self._clientes.listar()

    def buscar_productos(self, texto: str) -> list[Producto]:
        return self._productos.buscar_parcial(texto)

    def buscar_clientes(self, texto: str) -> list[Cliente]:
        return self._clientes.buscar_parcial(texto)

    def dar_baja_producto(self, codigo: str) -> Producto:
        return self._productos.cambiar_estado(codigo, Estado.INACTIVO)

    def dar_baja_cliente(self, identificacion: RUC | str) -> Cliente:
        return self._clientes.cambiar_estado(identificacion, Estado.INACTIVO)

    def crear_proforma_demo(self) -> Proforma:
        cliente = next(
            (item for item in self.listar_clientes() if item.estado == Estado.ACTIVO), None
        )
        producto = next(
            (item for item in self.listar_productos() if item.estado == Estado.ACTIVO), None
        )
        if cliente is None or producto is None:
            raise ValueError("Se necesita al menos un cliente y un producto activos")

        proforma = Proforma(numero="DEMO-001", cliente=cliente)
        proforma.agregar_item(
            ItemProforma(producto=producto, cantidad=1, tipo_cliente=cliente.tipo)
        )
        return proforma
