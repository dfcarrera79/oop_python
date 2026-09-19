import pytest

from proformas.ejemplos_semana7 import (
    Cola,
    Pila,
    Producto,
    RepositorioAtencion,
    RepositorioProductos,
)


@pytest.fixture
def pila() -> Pila[str]:
    return Pila(capacidad=2)


def test_pila_nueva_esta_vacia(pila: Pila[str]) -> None:
    assert pila.esta_vacia()
    assert pila.cantidad() == 0


def test_pila_respeta_orden_lifo(pila: Pila[str]) -> None:
    pila.apilar("primero")
    pila.apilar("ultimo")

    assert pila.desapilar() == "ultimo"
    assert pila.desapilar() == "primero"


def test_pila_llena_y_vacia_lanzan_excepcion(pila: Pila[str]) -> None:
    with pytest.raises(IndexError, match="vacia"):
        pila.desapilar()

    pila.apilar("uno")
    pila.apilar("dos")
    with pytest.raises(IndexError, match="llena"):
        pila.apilar("tres")


def test_cola_respeta_orden_fifo_y_reutiliza_espacio() -> None:
    cola: Cola[str] = Cola(capacidad=2)
    cola.encolar("Ana")
    cola.encolar("Luis")
    assert cola.desencolar() == "Ana"

    cola.encolar("Marta")  # Obliga a la cola circular a volver al indice cero.

    assert cola.desencolar() == "Luis"
    assert cola.desencolar() == "Marta"
    assert cola.esta_vacia()


def test_repositorio_productos_oculta_una_pila() -> None:
    repositorio = RepositorioProductos(capacidad=2)
    mouse = Producto("Mouse", 15.50, 10)
    teclado = Producto("Teclado", 25.00, 5)
    repositorio.agregar(mouse)
    repositorio.agregar(teclado)

    assert repositorio.retirar_ultimo() is teclado
    assert repositorio.retirar_ultimo() is mouse
    assert repositorio.esta_vacio()


def test_repositorio_atencion_oculta_una_cola() -> None:
    repositorio: RepositorioAtencion[str] = RepositorioAtencion(capacidad=2)
    repositorio.agregar("Ana")
    repositorio.agregar("Luis")

    assert repositorio.atender_siguiente() == "Ana"
    assert repositorio.atender_siguiente() == "Luis"
    assert repositorio.esta_vacio()
