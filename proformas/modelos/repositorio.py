"""Contratos e implementación del repositorio de clientes."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from proformas.modelos.cliente import Cliente
from proformas.modelos.valores import RUC


@runtime_checkable
class RepositorioClientes(Protocol):
    """Contrato de solo lectura sobre la colección de clientes."""

    def buscar(self, identificacion: RUC | str) -> Cliente | None:
        """Retorna el cliente con esa identificación o None."""
        ...

    def listar(self) -> list[Cliente]:
        """Retorna todos los clientes registrados."""
        ...


@runtime_checkable
class RegistroClientes(Protocol):
    """Contrato completo: lectura y escritura de clientes."""

    def registrar(self, cliente: Cliente) -> None:
        """Registra un cliente o rechaza una identificación duplicada."""
        ...

    def buscar(self, identificacion: RUC | str) -> Cliente | None:
        """Retorna el cliente con esa identificación o None."""
        ...

    def listar(self) -> list[Cliente]:
        """Retorna todos los clientes registrados."""
        ...


class RegistroClientesEnMemoria:
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

    def listar(self) -> list[Cliente]:
        return list(self._clientes.values())
