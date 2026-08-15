from collections.abc import Callable

from pydantic import ValidationError

from proformas.modelo import Cliente, Producto


def mostrar_casos_validos() -> None:
    """Construye y presenta objetos válidos."""
    print("\nCasos válidos")

    producto = Producto(
        codigo="P-0001",
        nombre="Laptop Lenovo",
        precio=850,
        impuesto=12,
    )
    cliente = Cliente(
        identificacion="1100001234",
        nombre="Ana Torres",
        direccion="Av. Loja y Sucre",
        telefono="0991234567",
        email="ana.torres@correo.com",
    )

    print(producto.resumen())
    print(cliente.resumen())


def mostrar_casos_invalidos() -> None:
    """Demuestra que el dominio rechaza estados inválidos."""
    print("\nCasos inválidos rechazados")
    intentos: list[tuple[str, Callable[[], object]]] = [
        (
            "precio negativo",
            lambda: Producto(codigo="P-0002", nombre="Teclado", precio=-10),
        ),
        (
            "impuesto mayor que 100",
            lambda: Producto(
                codigo="P-0003",
                nombre="Monitor",
                precio=180,
                impuesto=150,
            ),
        ),
        ("código vacío", lambda: Producto(codigo="", nombre="Mouse")),
        (
            "email inválido",
            lambda: Cliente(
                identificacion="1100000001",
                nombre="Luis",
                email="correo-sin-arroba",
            ),
        ),
    ]

    for descripcion, construir in intentos:
        try:
            construir()
        except ValidationError as error:
            mensaje = error.errors()[0]["msg"]
            print(f"[ok] {descripcion}: {mensaje}")


def main() -> None:
    print("Sistema de Gestión de Proformas - Fase 1")
    mostrar_casos_validos()
    mostrar_casos_invalidos()


if __name__ == "__main__":
    main()

