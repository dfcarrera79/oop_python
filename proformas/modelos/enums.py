"""Enumeraciones de dominio para el sistema de proformas."""

from __future__ import annotations

from enum import StrEnum


class Estado(StrEnum):
    """Estado de vida de un producto o cliente."""

    ACTIVO = "activo"
    INACTIVO = "inactivo"


class Talla(StrEnum):
    """Tallas disponibles para productos físicos."""

    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"
    UNICA = "única"


class TipoCliente(StrEnum):
    """Categoría comercial del cliente que determina su descuento."""

    PUBLICO = "público"
    MAYORISTA = "mayorista"
    MEDICO = "médico"

    @property
    def descuento_pct(self) -> float:
        """Porcentaje de descuento asociado al tipo de cliente."""
        _tasas: dict[TipoCliente, float] = {
            TipoCliente.PUBLICO: 15.0,
            TipoCliente.MAYORISTA: 35.0,
            TipoCliente.MEDICO: 40.0,
        }
        return _tasas[self]
