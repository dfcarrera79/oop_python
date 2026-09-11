"""Enumeraciones compartidas por las entidades del dominio."""

from enum import StrEnum


class Estado(StrEnum):
    ACTIVO = "activo"
    INACTIVO = "inactivo"


class Talla(StrEnum):
    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"
    UNICA = "única"


class TipoCliente(StrEnum):
    PUBLICO = "público"
    MAYORISTA = "mayorista"
    MEDICO = "médico"

    @property
    def descuento_pct(self) -> float:
        tasas: dict[TipoCliente, float] = {
            TipoCliente.PUBLICO: 15.0,
            TipoCliente.MAYORISTA: 35.0,
            TipoCliente.MEDICO: 40.0,
        }
        return tasas[self]
