"""Fachada compatible para modelos trasladados al paquete ``dominio``."""

from proformas.dominio import (
    RUC,
    AtributosDigitales,
    AtributosFisicos,
    Cliente,
    Email,
    Estado,
    ItemProforma,
    Monto,
    Producto,
    Proforma,
    Talla,
    TipoCliente,
)

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
