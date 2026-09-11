"""Entidad cliente."""

from pydantic import BaseModel, ConfigDict, Field, field_validator

from proformas.dominio.enumeraciones import Estado, TipoCliente
from proformas.dominio.valores import RUC, Email


class Cliente(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")
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
