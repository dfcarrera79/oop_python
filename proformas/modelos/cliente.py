"""Entidad de cliente."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from proformas.modelos.enums import Estado, TipoCliente
from proformas.modelos.valores import RUC, Email


class Cliente(BaseModel):
    """Persona o empresa que solicita una proforma."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    identificacion: RUC = Field(frozen=True)
    nombre: str
    direccion: str = ""
    telefono: str = ""
    email: Email = Email("")
    tipo: TipoCliente = TipoCliente.PUBLICO
    estado: Estado = Estado.ACTIVO

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        if not valor:
            raise ValueError("El nombre no puede estar vacío")
        return valor
