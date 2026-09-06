"""Coordinación de la sesión en memoria de la fase 4."""

from proformas.modelos import (
    RUC,
    Cliente,
    Estado,
    ItemProforma,
    Producto,
    Proforma,
    RegistroClientes,
    RegistroClientesEnMemoria,
)


class AplicacionProformas:
    """Coordina operaciones sin conocer detalles de consola."""

    def __init__(self, registro: RegistroClientes | None = None) -> None:
        self._productos: list[Producto] = []
        self._clientes: RegistroClientes = registro or RegistroClientesEnMemoria()

    def registrar_producto(self, producto: Producto) -> None:
        self._productos.append(producto)

    def registrar_cliente(self, cliente: Cliente) -> None:
        self._clientes.registrar(cliente)

    def listar_productos(self) -> list[Producto]:
        return list(self._productos)

    def listar_clientes(self) -> list[Cliente]:
        return self._clientes.listar()

    def dar_baja_producto(self, codigo: str) -> Producto:
        codigo = codigo.strip()
        producto = next((item for item in self._productos if item.codigo == codigo), None)
        if producto is None:
            raise LookupError(f"No existe el producto {codigo}")
        producto.estado = Estado.INACTIVO
        return producto

    def dar_baja_cliente(self, identificacion: RUC | str) -> Cliente:
        cliente = self._clientes.buscar(identificacion)
        if cliente is None:
            raise LookupError(f"No existe el cliente {identificacion}")
        cliente.estado = Estado.INACTIVO
        return cliente

    def crear_proforma_demo(self) -> Proforma:
        cliente = next(
            (item for item in self.listar_clientes() if item.estado == Estado.ACTIVO), None
        )
        producto = next((item for item in self._productos if item.estado == Estado.ACTIVO), None)
        if cliente is None or producto is None:
            raise ValueError("Se necesita al menos un cliente y un producto activos")

        proforma = Proforma(numero="DEMO-001", cliente=cliente)
        proforma.agregar_item(
            ItemProforma(
                producto=producto,
                cantidad=1,
                tipo_cliente=cliente.tipo,
            )
        )
        return proforma
