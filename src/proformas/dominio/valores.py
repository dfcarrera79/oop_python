"""Objetos de valor inmutables del dominio."""

from decimal import ROUND_HALF_UP, Decimal, DecimalException

from pydantic import ConfigDict, RootModel, field_validator


class Email(RootModel[str]):
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
