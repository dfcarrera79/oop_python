"""Entidad producto."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator

from proformas.dominio.enumeraciones import Estado
from proformas.dominio.valores import Monto

TASAS_IVA_DISPONIBLES = (0.0, 15.0)


def calcular_precio_sin_iva(
    precio_ingresado: object, iva_pct: float, *, incluye_iva: bool
) -> Monto:
    """Normaliza el precio para almacenarlo siempre sin impuestos."""
    precio = Monto(precio_ingresado)
    if not incluye_iva or iva_pct == 0:
        return precio
    factor_iva = Decimal("1") + Decimal(str(iva_pct)) / Decimal("100")
    return Monto(precio.root / factor_iva)


class Producto(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )
    codigo: str
    nombre: str
    descripcion: str = ""
    precio: Monto = Monto(0)
    iva_pct: float = 15.0
    estado: Estado = Estado.ACTIVO

    @field_validator("codigo", mode="before")
    @classmethod
    def validar_codigo(cls, valor: object) -> object:
        if isinstance(valor, str):
            valor = valor.strip().upper()
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
