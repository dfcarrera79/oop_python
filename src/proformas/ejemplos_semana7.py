"""Ejemplos de TDA lineales, Repository y pruebas para la semana 7."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Producto:
    """Producto minimo para concentrar el ejemplo en las estructuras de datos."""

    nombre: str
    precio: float
    stock: int


class Pila[T]:
    """Pila LIFO implementada sobre una lista de capacidad fija."""

    def __init__(self, capacidad: int) -> None:
        if capacidad <= 0:
            raise ValueError("La capacidad debe ser mayor que cero")
        self._elementos: list[T | None] = [None] * capacidad
        self._cantidad = 0

    def apilar(self, elemento: T) -> None:
        if self._cantidad == len(self._elementos):
            raise IndexError("La pila esta llena")
        self._elementos[self._cantidad] = elemento
        self._cantidad += 1

    def desapilar(self) -> T:
        if self.esta_vacia():
            raise IndexError("La pila esta vacia")
        self._cantidad -= 1
        elemento = self._elementos[self._cantidad]
        self._elementos[self._cantidad] = None
        assert elemento is not None
        return elemento

    def esta_vacia(self) -> bool:
        return self._cantidad == 0

    def cantidad(self) -> int:
        return self._cantidad


class Cola[T]:
    """Cola FIFO circular implementada sobre una lista de capacidad fija."""

    def __init__(self, capacidad: int) -> None:
        if capacidad <= 0:
            raise ValueError("La capacidad debe ser mayor que cero")
        self._elementos: list[T | None] = [None] * capacidad
        self._frente = 0
        self._cantidad = 0

    def encolar(self, elemento: T) -> None:
        if self._cantidad == len(self._elementos):
            raise IndexError("La cola esta llena")
        posicion_final = (self._frente + self._cantidad) % len(self._elementos)
        self._elementos[posicion_final] = elemento
        self._cantidad += 1

    def desencolar(self) -> T:
        if self.esta_vacia():
            raise IndexError("La cola esta vacia")
        elemento = self._elementos[self._frente]
        self._elementos[self._frente] = None
        self._frente = (self._frente + 1) % len(self._elementos)
        self._cantidad -= 1
        assert elemento is not None
        return elemento

    def esta_vacia(self) -> bool:
        return self._cantidad == 0

    def cantidad(self) -> int:
        return self._cantidad


class RepositorioProductos:
    """Repository que oculta la pila usada para almacenar productos."""

    def __init__(self, capacidad: int) -> None:
        self._pila: Pila[Producto] = Pila(capacidad)

    def agregar(self, producto: Producto) -> None:
        self._pila.apilar(producto)

    def retirar_ultimo(self) -> Producto:
        return self._pila.desapilar()

    def esta_vacio(self) -> bool:
        return self._pila.esta_vacia()


class RepositorioAtencion[T]:
    """Repository que oculta una cola y atiende objetos en orden FIFO."""

    def __init__(self, capacidad: int) -> None:
        self._cola: Cola[T] = Cola(capacidad)

    def agregar(self, elemento: T) -> None:
        self._cola.encolar(elemento)

    def atender_siguiente(self) -> T:
        return self._cola.desencolar()

    def esta_vacio(self) -> bool:
        return self._cola.esta_vacia()


def ejecutar_demostracion() -> None:
    mouse = Producto("Mouse", 15.50, 10)
    teclado = Producto("Teclado", 25.00, 5)

    repositorio = RepositorioProductos(capacidad=2)
    repositorio.agregar(mouse)
    repositorio.agregar(teclado)
    print("Pila (LIFO):", repositorio.retirar_ultimo().nombre, "sale primero")

    turnos: RepositorioAtencion[str] = RepositorioAtencion(capacidad=2)
    turnos.agregar("Ana")
    turnos.agregar("Luis")
    print("Cola (FIFO):", turnos.atender_siguiente(), "sale primero")


if __name__ == "__main__":
    ejecutar_demostracion()
