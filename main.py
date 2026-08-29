"""Demostración de consola de la semana 3."""

from collections.abc import Callable

from pydantic import ValidationError

from proformas.modelo import (
    RUC,
    Cliente,
    Email,
    ItemProforma,
    Monto,
    Producto,
    ProductoDigital,
    ProductoFisico,
    Proforma,
    RegistroClientesEnMemoria,
)


def mostrar_casos_validos() -> None:
    """Construye y presenta objetos válidos."""
    print("\nCasos válidos")

    producto_fisico = ProductoFisico(
        codigo="P-0001",
        nombre="Laptop Lenovo",
        precio=850,
        impuesto_pct=12,
        peso_kg=1.8,
    )
    producto_digital = ProductoDigital(
        codigo="P-0002",
        nombre="Licencia de ofimática",
        precio=45,
        tamanio_mb=750,
    )
    cliente = Cliente(
        identificacion="1100001234",
        nombre="Ana Torres",
        direccion="Av. Loja y Sucre",
        telefono="0991234567",
        email="ana.torres@correo.com",
    )
    proforma = Proforma(numero="PRO-0001", cliente=cliente)
    registro = RegistroClientesEnMemoria()
    registro.registrar(cliente)
    proforma.agregar_item(ItemProforma(producto=producto_fisico, cantidad=1, descuento_pct=5))
    proforma.agregar_item(ItemProforma(producto=producto_digital, cantidad=2))

    print(producto_fisico.resumen())
    print(producto_digital.resumen())
    print(cliente.resumen())
    print(proforma.resumen())
    print(f"Subtotal: ${proforma.subtotal():.2f}")
    print(f"Impuesto: ${proforma.impuesto():.2f}")
    print(f"Total: ${proforma.total():.2f}")
    print(f"Email por valor: {cliente.email == Email('ana.torres@correo.com')}")
    print(f"Representación del precio: {producto_fisico.precio!r}")
    print(f"Datos serializados: {cliente.model_dump()}")
    print(f"Cliente registrado: {registro.buscar('1100001234') is cliente}")


def mostrar_casos_invalidos() -> None:
    """Demuestra que el dominio rechaza estados inválidos."""
    print("\nCasos inválidos rechazados")
    registro = RegistroClientesEnMemoria()
    registro.registrar(Cliente(identificacion="1100000002", nombre="Cliente registrado"))
    intentos: list[tuple[str, Callable[[], object]]] = [
        (
            "precio negativo",
            lambda: Producto(codigo="P-0003", nombre="Teclado", precio=-10),
        ),
        (
            "impuesto mayor que 100",
            lambda: Producto(
                codigo="P-0004",
                nombre="Monitor",
                precio=180,
                impuesto_pct=150,
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
        (
            "cantidad no positiva",
            lambda: ItemProforma(
                producto=ProductoDigital(
                    codigo="P-0005",
                    nombre="Manual digital",
                    tamanio_mb=8,
                ),
                cantidad=0,
            ),
        ),
        (
            "producto inactivo",
            lambda: ItemProforma(
                producto=ProductoFisico(
                    codigo="P-0006",
                    nombre="Monitor descontinuado",
                    peso_kg=4.2,
                    activo=False,
                ),
                cantidad=1,
            ),
        ),
        ("identificación inválida", lambda: RUC("ABC0012345")),
        ("monto negativo", lambda: Monto(-1)),
        (
            "identificación duplicada",
            lambda: registro.registrar(
                Cliente(identificacion="1100000002", nombre="Cliente duplicado")
            ),
        ),
    ]

    for descripcion, construir in intentos:
        try:
            construir()
        except (ValidationError, ValueError) as error:
            mensaje = error.errors()[0]["msg"] if isinstance(error, ValidationError) else str(error)
            print(f"[ok] {descripcion}: {mensaje}")


def main() -> None:
    print("Sistema de Gestión de Proformas - Fase 3")
    mostrar_casos_validos()
    mostrar_casos_invalidos()


if __name__ == "__main__":
    main()
