"""Punto de entrada de la aplicación SQLite de la fase 5."""

import sys

from proformas.aplicacion import AplicacionProformas
from proformas.modelo import AtributosFisicos, Cliente, Producto, Talla, TipoCliente
from proformas.presentacion.formateadores import formatear_detalle_proforma
from proformas.presentacion.menu import MenuConsola


def crear_aplicacion_demo() -> AplicacionProformas:
    """Abre la base local y agrega datos iniciales solo cuando no existen."""
    aplicacion = AplicacionProformas()
    if not any(item.codigo == "P-0001" for item in aplicacion.buscar_productos("P-0001")):
        aplicacion.registrar_producto(
            Producto(
                codigo="P-0001",
                nombre="Faja Lumbar",
                precio=85,
                iva_pct=15,
                extras=AtributosFisicos(peso_kg=0.4, talla=Talla.M),
            )
        )
    if not any(
        str(item.identificacion) == "1100001234"
        for item in aplicacion.buscar_clientes("1100001234")
    ):
        aplicacion.registrar_cliente(
            Cliente(
                identificacion="1100001234",
                nombre="Ana Torres",
                email="ana.torres@correo.com",
                tipo=TipoCliente.MEDICO,
            )
        )
    return aplicacion


def main() -> None:
    """Ejecuta el menú o una demostración no interactiva."""
    aplicacion = crear_aplicacion_demo()
    if "--demo" in sys.argv:
        print("Sistema de Gestión de Proformas - Fase 5 (SQLite)")
        print(formatear_detalle_proforma(aplicacion.crear_proforma_demo()))
        return
    MenuConsola(aplicacion).ejecutar()


if __name__ == "__main__":
    main()
