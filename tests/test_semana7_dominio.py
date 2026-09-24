"""Pruebas unitarias para la integración de TDA lineales con las entidades de dominio."""

import pytest

from proformas.dominio.clientes import Cliente
from proformas.dominio.enumeraciones import TipoCliente
from proformas.dominio.productos import Producto
from proformas.dominio.valores import RUC, Monto
from proformas.ejemplos_semana7_dominio import (
    RepositorioColaAtencionClientes,
    RepositorioLoteProductos,
)


@pytest.fixture
def producto_laptop() -> Producto:
    return Producto(
        codigo="LAP-01",
        nombre="Laptop ThinkPad",
        precio=Monto("950.00"),
    )


@pytest.fixture
def producto_mouse() -> Producto:
    return Producto(
        codigo="MOU-02",
        nombre="Mouse Logitech",
        precio=Monto("25.00"),
    )


@pytest.fixture
def cliente_empresa() -> Cliente:
    return Cliente(
        identificacion=RUC("1790011674001"),
        nombre="Distribuidora Médica S.A.",
        tipo=TipoCliente.MAYORISTA,
    )


@pytest.fixture
def cliente_persona() -> Cliente:
    return Cliente(
        identificacion=RUC("1710034065"),
        nombre="Carlos Mendoza",
        tipo=TipoCliente.PUBLICO,
    )


def test_repositorio_lote_productos_lifo(
    producto_laptop: Producto, producto_mouse: Producto
) -> None:
    lote = RepositorioLoteProductos(capacidad=2)
    assert lote.esta_vacio()

    lote.apilar_producto(producto_laptop)
    lote.apilar_producto(producto_mouse)
    assert lote.cantidad() == 2

    # LIFO: El último producto agregado debe ser el primero en salir
    producto_tope = lote.retirar_producto_tope()
    assert producto_tope is producto_mouse
    assert producto_tope.codigo == "MOU-02"

    segundo_producto = lote.retirar_producto_tope()
    assert segundo_producto is producto_laptop
    assert segundo_producto.codigo == "LAP-01"

    assert lote.esta_vacio()


def test_repositorio_cola_clientes_fifo(
    cliente_empresa: Cliente, cliente_persona: Cliente
) -> None:
    cola = RepositorioColaAtencionClientes(capacidad=2)
    assert cola.esta_vacia()

    cola.registrar_llegada(cliente_empresa)
    cola.registrar_llegada(cliente_persona)
    assert cola.clientes_en_espera() == 2

    # FIFO: El primer cliente que llegó debe ser el primero en ser atendido
    primer_atendido = cola.atender_siguiente()
    assert primer_atendido is cliente_empresa
    assert str(primer_atendido.identificacion) == "1790011674001"

    segundo_atendido = cola.atender_siguiente()
    assert segundo_atendido is cliente_persona
    assert str(segundo_atendido.identificacion) == "1710034065"

    assert cola.esta_vacia()
