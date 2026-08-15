from pydantic._internal import _known_annotated_metadata
from pydantic import BaseModel, ConfigDict, field_validator


class Producto(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True,
        extra="forbid",
    )

    codigo: str
    nombre: str
    descripcion: str = ""
    precio: float = 0.0
    impuesto: float = 0.0
    activo: bool = True

    @field_validator("codigo")
    @classmethod
    def validar_codigo(cls, valor: str) -> str:
        if not valor: 
            raise ValueError("El código no puede estar vacio")
        return valor.strip()
    
    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        if not valor: 
            raise ValueError("El nombre no puede estar vacio")
        return valor.strip()
    
    @field_validator("impuesto")
    @classmethod
    def validar_impuesto(cls, valor: float) -> float:
        if not (0 < valor <= 100):
            raise ValueError("El impuesto debe estar entre 0 y 100")
        return round(valor, 2)
        
    def resumen(self) -> str:
        estado = "Activo" if self.activo else "Inactivo"
        return (
            f"Código: {self.codigo}\n"
            f"Nombre: {self.nombre}\n"
            f"Precio: {self.precio:.2f}\n"
            f"Impuesto: {self.impuesto:.2f}\n"
            f"Estado: {estado}\n"
        )
        

class Cliente(BaseModel):
    """Persona o empresa que solicita una proforma."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    identificacion: str
    nombre: str
    direccion: str = ""
    telefono: str = ""
    email: str = ""
    activo: bool = True

    @field_validator("identificacion")
    @classmethod
    def validar_identificacion(cls, valor: str) -> str:
        if not valor:
            raise ValueError("La identificación no puede estar vacía")
        return valor

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        if not valor:
            raise ValueError("El nombre no puede estar vacío")
        return valor

    @field_validator("email")
    @classmethod
    def validar_email(cls, valor: str) -> str:
        if valor and ("@" not in valor or "." not in valor.rsplit("@", maxsplit=1)[-1]):
            raise ValueError("El email no tiene un formato válido")
        return valor

    def resumen(self) -> str:
        """Retorna una representación legible sin imprimirla."""
        estado = "activo" if self.activo else "inactivo"
        return (
            f"[{self.identificacion}] {self.nombre} - {self.direccion} - "
            f"{self.telefono} - {self.email} - {estado}"
        )