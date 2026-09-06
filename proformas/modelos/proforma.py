"""Entidades de proforma y sus líneas de ítems."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from proformas.modelos.cliente import Cliente
from proformas.modelos.enums import Estado, TipoCliente
from proformas.modelos.producto import Producto


class ItemProforma(BaseModel):
    """Línea de una proforma con sus importes calculados."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    producto: Producto
    cantidad: int
    tipo_cliente: TipoCliente | None = None

    @field_validator("producto")
    @classmethod
    def validar_producto_activo(cls, valor: Producto) -> Producto:
        if valor.estado != Estado.ACTIVO:
            raise ValueError("El producto debe estar activo")
        return valor

    @field_validator("cantidad")
    @classmethod
    def validar_cantidad(cls, valor: int) -> int:
        if valor <= 0:
            raise ValueError("La cantidad debe ser mayor que cero")
        return valor

    @property
    def descuento_pct(self) -> float:
        """Porcentaje de descuento según el tipo de cliente (0 si no se especifica)."""
        return self.tipo_cliente.descuento_pct if self.tipo_cliente is not None else 0.0

    def subtotal(self) -> float:
        """Calcula el importe después del descuento y antes del IVA."""
        importe_bruto = float(self.producto.precio) * self.cantidad
        return importe_bruto * (1 - self.descuento_pct / 100)

    def impuesto(self) -> float:
        """Calcula el IVA sobre el subtotal descontado."""
        return self.subtotal() * self.producto.iva_pct / 100

    def total(self) -> float:
        """Calcula el importe final del ítem."""
        return self.subtotal() + self.impuesto()


class Proforma(BaseModel):
    """Cotización solicitada por un cliente y compuesta por ítems."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    numero: str
    cliente: Cliente
    items: list[ItemProforma] = Field(default_factory=list)

    @field_validator("numero")
    @classmethod
    def validar_numero(cls, valor: str) -> str:
        if not valor:
            raise ValueError("El número no puede estar vacío")
        return valor

    def agregar_item(self, item: ItemProforma) -> None:
        """Incorpora un ítem mediante una asignación validada."""
        self.items = [*self.items, item]

    def subtotal(self) -> float:
        """Suma los subtotales de todos los ítems."""
        return sum((item.subtotal() for item in self.items), start=0.0)

    def impuesto(self) -> float:
        """Suma los impuestos de todos los ítems."""
        return sum((item.impuesto() for item in self.items), start=0.0)

    def total(self) -> float:
        """Suma los totales de todos los ítems."""
        return sum((item.total() for item in self.items), start=0.0)
