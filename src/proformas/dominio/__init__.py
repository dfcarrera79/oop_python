"""Modelos y reglas del dominio, independientes de SQLite y la consola."""

from proformas.dominio.clientes import Cliente
from proformas.dominio.enumeraciones import Estado, Talla, TipoCliente
from proformas.dominio.productos import AtributosDigitales, AtributosFisicos, Producto
from proformas.dominio.proformas import ItemProforma, Proforma
from proformas.dominio.valores import RUC, Email, Monto

__all__ = [
    "AtributosDigitales",
    "AtributosFisicos",
    "Cliente",
    "Email",
    "Estado",
    "ItemProforma",
    "Monto",
    "Producto",
    "Proforma",
    "RUC",
    "Talla",
    "TipoCliente",
]
