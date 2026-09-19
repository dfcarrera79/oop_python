"""Agregado proforma y sus cálculos."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator

from proformas.dominio.clientes import Cliente
from proformas.dominio.enumeraciones import Estado, Talla, TipoCliente
from proformas.dominio.productos import Producto


class ItemProforma(BaseModel):
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    producto: Producto
    cantidad: int
    tipo_cliente: TipoCliente | None = None
    talla: Talla | None = None

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
        return self.tipo_cliente.descuento_pct if self.tipo_cliente is not None else 0.0

    def subtotal(self) -> float:
        importe_bruto = float(self.producto.precio) * self.cantidad
        return importe_bruto * (1 - self.descuento_pct / 100)

    def impuesto(self) -> float:
        return self.subtotal() * self.producto.iva_pct / 100

    def total(self) -> float:
        return self.subtotal() + self.impuesto()


class Proforma(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")
    numero: str
    cliente: Cliente
    fecha: date = Field(default_factory=date.today)
    items: list[ItemProforma] = Field(default_factory=list)
    observaciones: str = ""
    instrucciones_pago: str = ""

    @field_validator("numero")
    @classmethod
    def validar_numero(cls, valor: str) -> str:
        if not valor:
            raise ValueError("El número no puede estar vacío")
        return valor

    def subtotal(self) -> float:
        return sum((item.subtotal() for item in self.items), start=0.0)

    def impuesto(self) -> float:
        return sum((item.impuesto() for item in self.items), start=0.0)

    def total(self) -> float:
        return sum((item.total() for item in self.items), start=0.0)
