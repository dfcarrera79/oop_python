from decimal import Decimal

import pytest
from pydantic import ValidationError

from proformas.dominio.productos import Producto, calcular_precio_sin_iva


def test_producto_normaliza_codigo_y_precio() -> None:
    producto = Producto(codigo="  lap-01 ", nombre="Laptop", precio="999.995")

    assert producto.codigo == "LAP-01"
    assert producto.precio == Decimal("1000.00")


def test_producto_rechaza_codigo_vacio() -> None:
    with pytest.raises(ValidationError, match="código no puede estar vacío"):
        Producto(codigo="   ", nombre="Laptop")


def test_calcular_precio_sin_iva() -> None:
    precio = calcular_precio_sin_iva("115", 15, incluye_iva=True)

    assert precio == Decimal("100.00")
