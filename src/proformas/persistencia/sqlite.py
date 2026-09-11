"""Catálogos genéricos respaldados exclusivamente por SQLite."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable, Iterable
from pathlib import Path
from types import TracebackType
from typing import Protocol, TypeVar, runtime_checkable

from proformas.dominio import (
    RUC,
    AtributosDigitales,
    AtributosFisicos,
    Cliente,
    Estado,
    Producto,
    Talla,
    TipoCliente,
)

EntidadT = TypeVar("EntidadT")


@runtime_checkable
class CatalogoProductos(Protocol):
    def registrar(self, producto: Producto) -> None: ...
    def buscar(self, codigo: str) -> Producto | None: ...
    def buscar_parcial(self, texto: str) -> list[Producto]: ...
    def listar(self) -> list[Producto]: ...
    def cambiar_estado(self, codigo: str, estado: Estado) -> Producto: ...


@runtime_checkable
class RegistroClientes(Protocol):
    def registrar(self, cliente: Cliente) -> None: ...
    def buscar(self, identificacion: RUC | str) -> Cliente | None: ...
    def buscar_parcial(self, texto: str) -> list[Cliente]: ...
    def listar(self) -> list[Cliente]: ...
    def cambiar_estado(self, identificacion: RUC | str, estado: Estado) -> Cliente: ...


class ColeccionSQLite[EntidadT]:
    """Base genérica que convierte filas SQLite en colecciones tipadas."""

    def __init__(self, ruta_bd: str | Path) -> None:
        self.ruta_bd = str(ruta_bd)
        if self.ruta_bd != ":memory:":
            Path(self.ruta_bd).parent.mkdir(parents=True, exist_ok=True)
        self._conexion = sqlite3.connect(self.ruta_bd)
        self._conexion.row_factory = sqlite3.Row
        self._crear_esquema()

    def _crear_esquema(self) -> None:
        raise NotImplementedError

    def _como_lista(
        self, filas: Iterable[sqlite3.Row], convertir: Callable[[sqlite3.Row], EntidadT]
    ) -> list[EntidadT]:
        return [convertir(fila) for fila in filas]

    def cerrar(self) -> None:
        self._conexion.close()

    def __enter__(self) -> ColeccionSQLite[EntidadT]:
        return self

    def __exit__(
        self,
        tipo: type[BaseException] | None,
        valor: BaseException | None,
        traza: TracebackType | None,
    ) -> None:
        self.cerrar()


class CatalogoProductosSQLite(ColeccionSQLite[Producto]):
    """Catálogo persistente con código único y búsquedas parciales."""

    def _crear_esquema(self) -> None:
        self._conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS productos (
                codigo TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                descripcion TEXT NOT NULL DEFAULT '',
                precio TEXT NOT NULL,
                iva_pct REAL NOT NULL,
                estado TEXT NOT NULL,
                tipo_extra TEXT,
                peso_kg REAL,
                talla TEXT,
                tamanio_mb REAL
            )
            """
        )
        self._conexion.commit()

    def registrar(self, producto: Producto) -> None:
        tipo_extra, peso, talla, tamanio = self._descomponer_extras(producto)
        try:
            with self._conexion:
                self._conexion.execute(
                    """
                    INSERT INTO productos
                    (codigo, nombre, descripcion, precio, iva_pct, estado,
                     tipo_extra, peso_kg, talla, tamanio_mb)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        producto.codigo,
                        producto.nombre,
                        producto.descripcion,
                        str(producto.precio),
                        producto.iva_pct,
                        producto.estado.value,
                        tipo_extra,
                        peso,
                        talla,
                        tamanio,
                    ),
                )
        except sqlite3.IntegrityError as error:
            raise ValueError(f"ya existe un producto con código {producto.codigo}") from error

    def buscar(self, codigo: str) -> Producto | None:
        fila = self._conexion.execute(
            "SELECT * FROM productos WHERE codigo = ?", (codigo.strip(),)
        ).fetchone()
        return self._desde_fila(fila) if fila else None

    def buscar_parcial(self, texto: str) -> list[Producto]:
        patron = f"%{texto.strip()}%"
        filas = self._conexion.execute(
            """
            SELECT * FROM productos
            WHERE codigo LIKE ? COLLATE NOCASE
               OR nombre LIKE ? COLLATE NOCASE
               OR descripcion LIKE ? COLLATE NOCASE
            ORDER BY codigo
            """,
            (patron, patron, patron),
        ).fetchall()
        return self._como_lista(filas, self._desde_fila)

    def listar(self) -> list[Producto]:
        filas = self._conexion.execute("SELECT * FROM productos ORDER BY codigo").fetchall()
        return self._como_lista(filas, self._desde_fila)

    def mapa_por_codigo(self) -> dict[str, Producto]:
        """Representa el catálogo como Map/dict para el laboratorio."""
        return {producto.codigo: producto for producto in self.listar()}

    def codigos(self) -> set[str]:
        """Retorna códigos únicos como Set/set para el laboratorio."""
        return set(self.mapa_por_codigo())

    def cambiar_estado(self, codigo: str, estado: Estado) -> Producto:
        with self._conexion:
            cursor = self._conexion.execute(
                "UPDATE productos SET estado = ? WHERE codigo = ?",
                (estado.value, codigo.strip()),
            )
        if cursor.rowcount == 0:
            raise LookupError(f"No existe el producto {codigo.strip()}")
        producto = self.buscar(codigo)
        assert producto is not None
        return producto

    @staticmethod
    def _descomponer_extras(
        producto: Producto,
    ) -> tuple[str | None, float | None, str | None, float | None]:
        if isinstance(producto.extras, AtributosFisicos):
            talla = producto.extras.talla.value if producto.extras.talla else None
            return "fisico", producto.extras.peso_kg, talla, None
        if isinstance(producto.extras, AtributosDigitales):
            return "digital", None, None, producto.extras.tamanio_mb
        return None, None, None, None

    @staticmethod
    def _desde_fila(fila: sqlite3.Row) -> Producto:
        extras = None
        if fila["tipo_extra"] == "fisico":
            talla = Talla(fila["talla"]) if fila["talla"] else None
            extras = AtributosFisicos(peso_kg=fila["peso_kg"], talla=talla)
        elif fila["tipo_extra"] == "digital":
            extras = AtributosDigitales(tamanio_mb=fila["tamanio_mb"])
        return Producto(
            codigo=fila["codigo"],
            nombre=fila["nombre"],
            descripcion=fila["descripcion"],
            precio=fila["precio"],
            iva_pct=fila["iva_pct"],
            estado=fila["estado"],
            extras=extras,
        )


class RegistroClientesSQLite(ColeccionSQLite[Cliente]):
    """Registro persistente con identificación única y búsqueda parcial."""

    def _crear_esquema(self) -> None:
        self._conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS clientes (
                identificacion TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                direccion TEXT NOT NULL DEFAULT '',
                telefono TEXT NOT NULL DEFAULT '',
                email TEXT NOT NULL DEFAULT '',
                tipo TEXT NOT NULL,
                estado TEXT NOT NULL
            )
            """
        )
        self._conexion.commit()

    def registrar(self, cliente: Cliente) -> None:
        try:
            with self._conexion:
                self._conexion.execute(
                    """
                    INSERT INTO clientes
                    (identificacion, nombre, direccion, telefono, email, tipo, estado)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(cliente.identificacion),
                        cliente.nombre,
                        cliente.direccion,
                        cliente.telefono,
                        str(cliente.email),
                        cliente.tipo.value,
                        cliente.estado.value,
                    ),
                )
        except sqlite3.IntegrityError as error:
            raise ValueError(
                f"ya existe un cliente con identificación {cliente.identificacion}"
            ) from error

    def buscar(self, identificacion: RUC | str) -> Cliente | None:
        clave = str(identificacion).strip()
        fila = self._conexion.execute(
            "SELECT * FROM clientes WHERE identificacion = ?", (clave,)
        ).fetchone()
        return self._desde_fila(fila) if fila else None

    def buscar_parcial(self, texto: str) -> list[Cliente]:
        patron = f"%{texto.strip()}%"
        filas = self._conexion.execute(
            """
            SELECT * FROM clientes
            WHERE identificacion LIKE ? COLLATE NOCASE
               OR nombre LIKE ? COLLATE NOCASE
               OR email LIKE ? COLLATE NOCASE
            ORDER BY identificacion
            """,
            (patron, patron, patron),
        ).fetchall()
        return self._como_lista(filas, self._desde_fila)

    def listar(self) -> list[Cliente]:
        filas = self._conexion.execute("SELECT * FROM clientes ORDER BY identificacion").fetchall()
        return self._como_lista(filas, self._desde_fila)

    def mapa_por_identificacion(self) -> dict[RUC, Cliente]:
        return {cliente.identificacion: cliente for cliente in self.listar()}

    def identificaciones(self) -> set[RUC]:
        return set(self.mapa_por_identificacion())

    def cambiar_estado(self, identificacion: RUC | str, estado: Estado) -> Cliente:
        clave = str(identificacion).strip()
        with self._conexion:
            cursor = self._conexion.execute(
                "UPDATE clientes SET estado = ? WHERE identificacion = ?",
                (estado.value, clave),
            )
        if cursor.rowcount == 0:
            raise LookupError(f"No existe el cliente {clave}")
        cliente = self.buscar(clave)
        assert cliente is not None
        return cliente

    @staticmethod
    def _desde_fila(fila: sqlite3.Row) -> Cliente:
        return Cliente(
            identificacion=fila["identificacion"],
            nombre=fila["nombre"],
            direccion=fila["direccion"],
            telefono=fila["telefono"],
            email=fila["email"],
            tipo=TipoCliente(fila["tipo"]),
            estado=Estado(fila["estado"]),
        )
