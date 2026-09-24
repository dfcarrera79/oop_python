"""Ejemplo de integración de TDA lineales (Pila y Cola) con las entidades reales del dominio.

Demuestra cómo las estructuras genéricas Pila[T] y Cola[T] funcionan perfectamente
con los modelos Pydantic reales de la aplicación (Producto y Cliente).
"""

from proformas.dominio.clientes import Cliente
from proformas.dominio.enumeraciones import TipoCliente
from proformas.dominio.productos import Producto
from proformas.dominio.valores import RUC, Monto
from proformas.ejemplos_semana7 import Cola, Pila


class RepositorioLoteProductos:
    """Repository que gestiona un lote de productos en almacén usando una Pila (LIFO).

    En un estante físico, los productos se apilan verticalmente,
    por lo que el último producto colocado es el primero en ser descargado.
    """

    def __init__(self, capacidad: int) -> None:
        self._pila: Pila[Producto] = Pila(capacidad)

    def apilar_producto(self, producto: Producto) -> None:
        self._pila.apilar(producto)

    def retirar_producto_tope(self) -> Producto:
        return self._pila.desapilar()

    def esta_vacio(self) -> bool:
        return self._pila.esta_vacia()

    def cantidad(self) -> int:
        return self._pila.cantidad()


class RepositorioColaAtencionClientes:
    """Repository que gestiona el orden de atención de clientes en caja usando una Cola (FIFO).

    Garantiza que el primer cliente en llegar sea el primero en ser atendido
    para generar o pagar su proforma.
    """

    def __init__(self, capacidad: int) -> None:
        self._cola: Cola[Cliente] = Cola(capacidad)

    def registrar_llegada(self, cliente: Cliente) -> None:
        self._cola.encolar(cliente)

    def atender_siguiente(self) -> Cliente:
        return self._cola.desencolar()

    def esta_vacia(self) -> bool:
        return self._cola.esta_vacia()

    def clientes_en_espera(self) -> int:
        return self._cola.cantidad()


def ejecutar_demostracion_dominio() -> None:
    print("=== 1. Demostración Pila (LIFO) con Producto real del dominio ===")
    lote = RepositorioLoteProductos(capacidad=3)

    prod1 = Producto(
        codigo="LAP-01",
        nombre="Laptop Lenovo ThinkPad",
        precio=Monto("950.00"),
        iva_pct=15.0,
    )
    prod2 = Producto(
        codigo="MOU-02",
        nombre="Mouse Inalámbrico Logitech",
        precio=Monto("25.50"),
        iva_pct=15.0,
    )

    lote.apilar_producto(prod1)
    lote.apilar_producto(prod2)
    print(f"Productos apilados en el lote: {lote.cantidad()}")

    retirado = lote.retirar_producto_tope()
    print(
        f"LIFO: Se retira primero el último apilado -> {retirado.nombre} (Código: {retirado.codigo})"
    )
    print(f"Quedan en el lote: {lote.cantidad()} producto(s)\n")

    print("=== 2. Demostración Cola (FIFO) con Cliente real del dominio ===")
    cola_caja = RepositorioColaAtencionClientes(capacidad=3)

    cliente_empresa = Cliente(
        identificacion=RUC("1790011674001"),
        nombre="Distribuidora Médica S.A.",
        tipo=TipoCliente.MAYORISTA,
        direccion="Av. General Enríquez",
    )
    cliente_persona = Cliente(
        identificacion=RUC("1710034065"),
        nombre="Carlos Mendoza",
        tipo=TipoCliente.PUBLICO,
    )

    cola_caja.registrar_llegada(cliente_empresa)
    cola_caja.registrar_llegada(cliente_persona)
    print(f"Clientes en fila de espera: {cola_caja.clientes_en_espera()}")

    atendido = cola_caja.atender_siguiente()
    print(
        f"FIFO: Se atiende al primer cliente en llegar -> {atendido.nombre} "
        f"[RUC: {atendido.identificacion}] ({atendido.tipo.value})"
    )
    print(f"Clientes restantes en espera: {cola_caja.clientes_en_espera()}")


if __name__ == "__main__":
    ejecutar_demostracion_dominio()
