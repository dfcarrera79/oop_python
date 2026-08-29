"""Modelos de dominio de las semanas 1 a 3."""

from abc import ABC, abstractmethod
from decimal import ROUND_HALF_UP, Decimal, DecimalException

from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator


class Email(RootModel[str]):
    """Correo electrónico inmutable comparable por su valor."""

    model_config = ConfigDict(frozen=True)

    @field_validator("root", mode="before")
    @classmethod
    def validar_email(cls, valor: object) -> object:
        if not isinstance(valor, str):
            return valor
        valor = valor.strip()
        if valor and ("@" not in valor or "." not in valor.rsplit("@", maxsplit=1)[-1]):
            raise ValueError("El email no tiene un formato válido")
        if valor.startswith("@"):
            raise ValueError("El email no tiene un formato válido")
        return valor

    def __str__(self) -> str:
        return self.root

    def __repr__(self) -> str:
        return f"Email({self.root!r})"

    def __eq__(self, otro: object) -> bool:
        if isinstance(otro, Email):
            return self.root == otro.root
        if isinstance(otro, str):
            return self.root == otro
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.root)


class RUC(RootModel[str]):
    """Cédula o RUC ecuatoriano validado por formato."""

    model_config = ConfigDict(frozen=True)

    @field_validator("root", mode="before")
    @classmethod
    def validar_identificacion(cls, valor: object) -> object:
        if not isinstance(valor, str):
            return valor
        valor = valor.strip()
        if not valor:
            raise ValueError("La identificación no puede estar vacía")
        if not valor.isdigit() or len(valor) not in (10, 13):
            raise ValueError("La identificación debe contener 10 o 13 dígitos")
        return valor

    def __str__(self) -> str:
        return self.root

    def __repr__(self) -> str:
        return f"RUC({self.root!r})"

    def __eq__(self, otro: object) -> bool:
        if isinstance(otro, RUC):
            return self.root == otro.root
        if isinstance(otro, str):
            return self.root == otro
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.root)


class Monto(RootModel[Decimal]):
    """Importe monetario inmutable, no negativo y con dos decimales."""

    model_config = ConfigDict(frozen=True)

    @field_validator("root", mode="before")
    @classmethod
    def validar_monto(cls, valor: object) -> Decimal:
        try:
            monto = Decimal(str(valor))
        except (DecimalException, TypeError, ValueError) as error:
            raise ValueError("El monto debe ser un número válido") from error
        if not monto.is_finite():
            raise ValueError("El monto debe ser finito")
        if monto < 0:
            raise ValueError("El monto no puede ser negativo")
        return monto.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def __str__(self) -> str:
        return f"{self.root:.2f}"

    def __repr__(self) -> str:
        return f"Monto({str(self)!r})"

    def __format__(self, especificacion: str) -> str:
        return format(self.root, especificacion)

    def __float__(self) -> float:
        return float(self.root)

    def __eq__(self, otro: object) -> bool:
        if isinstance(otro, Monto):
            return self.root == otro.root
        if isinstance(otro, (Decimal, int, float)) and not isinstance(otro, bool):
            return self.root == Decimal(str(otro))
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.root)


class Producto(BaseModel):
    """Producto genérico disponible para una proforma."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    codigo: str
    nombre: str
    descripcion: str = ""
    precio: Monto = Monto(0)
    impuesto_pct: float = 0.0
    activo: bool = True

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

    @field_validator("impuesto_pct")
    @classmethod
    def validar_impuesto(cls, valor: float) -> float:
        if not 0 <= valor <= 100:
            raise ValueError("El impuesto debe estar entre 0 y 100")
        return valor

    def resumen(self) -> str:
        """Retorna una representación legible sin imprimirla."""
        estado = "activo" if self.activo else "inactivo"
        return (
            f"[{self.codigo}] {self.nombre} - ${self.precio:.2f} "
            f"(impuesto {self.impuesto_pct:.1f}%) - {estado}"
        )


class ProductoFisico(Producto):
    """Producto tangible cuyo peso se registra en kilogramos."""

    peso_kg: float

    @field_validator("peso_kg")
    @classmethod
    def validar_peso(cls, valor: float) -> float:
        if valor <= 0:
            raise ValueError("El peso debe ser mayor que cero")
        return valor


class ProductoDigital(Producto):
    """Producto descargable cuyo tamaño se registra en megabytes."""

    tamanio_mb: float

    @field_validator("tamanio_mb")
    @classmethod
    def validar_tamanio(cls, valor: float) -> float:
        if valor <= 0:
            raise ValueError("El tamaño debe ser mayor que cero")
        return valor


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
    activo: bool = True

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        if not valor:
            raise ValueError("El nombre no puede estar vacío")
        return valor

    def resumen(self) -> str:
        """Retorna una representación legible sin imprimirla."""
        estado = "activo" if self.activo else "inactivo"
        return (
            f"[{self.identificacion}] {self.nombre} - {self.direccion} - "
            f"{self.telefono} - {self.email} - {estado}"
        )


class RegistroClientes(ABC):
    """Contrato para registrar clientes sin repetir su identificación."""

    @abstractmethod
    def registrar(self, cliente: Cliente) -> None:
        """Registra un cliente o rechaza una identificación duplicada."""

    @abstractmethod
    def buscar(self, identificacion: RUC | str) -> Cliente | None:
        """Busca un cliente por cédula o RUC."""


class RegistroClientesEnMemoria(RegistroClientes):
    """Registro de clientes respaldado por un diccionario en memoria."""

    def __init__(self) -> None:
        self._clientes: dict[RUC, Cliente] = {}

    def registrar(self, cliente: Cliente) -> None:
        if cliente.identificacion in self._clientes:
            raise ValueError(f"ya existe un cliente con identificación {cliente.identificacion}")
        self._clientes[cliente.identificacion] = cliente

    def buscar(self, identificacion: RUC | str) -> Cliente | None:
        clave = identificacion if isinstance(identificacion, RUC) else RUC(identificacion)
        return self._clientes.get(clave)


class ItemProforma(BaseModel):
    """Línea de una proforma con sus importes calculados."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    producto: Producto
    cantidad: int
    descuento_pct: float = 0.0

    @field_validator("producto")
    @classmethod
    def validar_producto_activo(cls, valor: Producto) -> Producto:
        if not valor.activo:
            raise ValueError("El producto debe estar activo")
        return valor

    @field_validator("cantidad")
    @classmethod
    def validar_cantidad(cls, valor: int) -> int:
        if valor <= 0:
            raise ValueError("La cantidad debe ser mayor que cero")
        return valor

    @field_validator("descuento_pct")
    @classmethod
    def validar_descuento(cls, valor: float) -> float:
        if not 0 <= valor <= 100:
            raise ValueError("El descuento debe estar entre 0 y 100")
        return valor

    def subtotal(self) -> float:
        """Calcula el importe después del descuento y antes del impuesto."""
        importe_bruto = float(self.producto.precio) * self.cantidad
        return importe_bruto * (1 - self.descuento_pct / 100)

    def impuesto(self) -> float:
        """Calcula el impuesto sobre el subtotal descontado."""
        return self.subtotal() * self.producto.impuesto_pct / 100

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

    def resumen(self) -> str:
        """Retorna una representación legible sin imprimirla."""
        unidad = "ítem" if len(self.items) == 1 else "ítems"
        return (
            f"Proforma {self.numero} - {self.cliente.nombre} - "
            f"{len(self.items)} {unidad} - ${self.total():.2f}"
        )
