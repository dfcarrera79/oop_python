"""Entidad de producto."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, field_validator

from proformas.modelos.atributos import AtributosDigitales, AtributosFisicos
from proformas.modelos.enums import Estado
from proformas.modelos.valores import Monto


class Producto(BaseModel):
    """Producto disponible para una proforma."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    codigo: str
    nombre: str
    descripcion: str = ""
    precio: Monto = Monto(0)
    iva_pct: float = 15.0
    estado: Estado = Estado.ACTIVO
    extras: AtributosFisicos | AtributosDigitales | None = None

    @field_validator("codigo")
    @classmethod
    def validar_codigo(cls, valor: str) -> str:
        if not valor:
            raise ValueError("El código no puede estar vacío")
        return valor

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        if not valor:
            raise ValueError("El nombre no puede estar vacío")
        return valor

    @field_validator("iva_pct")
    @classmethod
    def validar_iva(cls, valor: float) -> float:
        if not 0 <= valor <= 100:
            raise ValueError("El IVA debe estar entre 0 y 100")
        return valor
