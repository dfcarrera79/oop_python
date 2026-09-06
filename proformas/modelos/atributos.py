"""Atributos extra por composición de productos."""

from __future__ import annotations

from dataclasses import dataclass

from proformas.modelos.enums import Talla


@dataclass(frozen=True)
class AtributosFisicos:
    """Características de un producto tangible."""

    peso_kg: float
    talla: Talla | None = None

    def __post_init__(self) -> None:
        if self.peso_kg <= 0:
            raise ValueError("El peso debe ser mayor que cero")


@dataclass(frozen=True)
class AtributosDigitales:
    """Características de un producto descargable."""

    tamanio_mb: float

    def __post_init__(self) -> None:
        if self.tamanio_mb <= 0:
            raise ValueError("El tamaño debe ser mayor que cero")
