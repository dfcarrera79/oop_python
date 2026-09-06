"""Modelos de dominio de las clases 1 a 4 organizados en módulos."""

from proformas.modelos.atributos import AtributosDigitales, AtributosFisicos
from proformas.modelos.cliente import Cliente
from proformas.modelos.enums import Estado, Talla, TipoCliente
from proformas.modelos.producto import Producto
from proformas.modelos.proforma import ItemProforma, Proforma
from proformas.modelos.repositorio import (
    RegistroClientes,
    RegistroClientesEnMemoria,
    RepositorioClientes,
)
from proformas.modelos.valores import RUC, Email, Monto

__all__ = [
    "RUC",
    "AtributosDigitales",
    "AtributosFisicos",
    "Cliente",
    "Email",
    "Estado",
    "ItemProforma",
    "Monto",
    "Producto",
    "Proforma",
    "RegistroClientes",
    "RegistroClientesEnMemoria",
    "RepositorioClientes",
    "Talla",
    "TipoCliente",
]
