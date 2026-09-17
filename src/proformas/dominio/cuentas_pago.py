"""Datos de pago reutilizables en las proformas."""

from pydantic import BaseModel, ConfigDict, field_validator


class CuentaPago(BaseModel):
    """Cuenta o modalidad de pago guardada por el usuario."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    id: int | None = None
    nombre: str
    instrucciones: str

    @field_validator("nombre", "instrucciones")
    @classmethod
    def validar_texto(cls, valor: str) -> str:
        if not valor:
            raise ValueError("El nombre y las instrucciones son obligatorios")
        return valor
