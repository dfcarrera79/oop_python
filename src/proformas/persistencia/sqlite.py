"""Catálogos genéricos respaldados exclusivamente por SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from proformas.dominio import RUC, Cliente, Estado, Producto, TipoCliente


class _BaseSQLite:
    """Inicialización compartida de las conexiones SQLite."""

    def __init__(self, ruta_bd: str | Path) -> None:
        self.ruta_bd = str(ruta_bd)
        if self.ruta_bd != ":memory:":
            Path(self.ruta_bd).parent.mkdir(parents=True, exist_ok=True)
        self._conexion = sqlite3.connect(self.ruta_bd)
        self._conexion.row_factory = sqlite3.Row
        self._conexion.execute("PRAGMA foreign_keys = ON")
        self._crear_esquema()

    def _crear_esquema(self) -> None:
        raise NotImplementedError

    def cerrar(self) -> None:
        self._conexion.close()


class CatalogoProductosSQLite(_BaseSQLite):
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
                estado TEXT NOT NULL
            )
            """
        )
        self._conexion.commit()

    def registrar(self, producto: Producto) -> None:
        try:
            with self._conexion:
                self._conexion.execute(
                    """
                    INSERT INTO productos
                    (codigo, nombre, descripcion, precio, iva_pct, estado)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        producto.codigo,
                        producto.nombre,
                        producto.descripcion,
                        str(producto.precio),
                        producto.iva_pct,
                        producto.estado.value,
                    ),
                )
        except sqlite3.IntegrityError as error:
            raise ValueError(f"ya existe un producto con código {producto.codigo}") from error

    def buscar(self, codigo: str) -> Producto | None:
        fila = self._conexion.execute(
            "SELECT * FROM productos WHERE codigo = ?", (codigo.strip().upper(),)
        ).fetchone()
        return self._desde_fila(fila) if fila else None

    def actualizar(self, producto: Producto) -> None:
        with self._conexion:
            cursor = self._conexion.execute(
                """
                UPDATE productos
                SET nombre = ?, descripcion = ?, precio = ?, iva_pct = ?, estado = ?
                WHERE codigo = ?
                """,
                (
                    producto.nombre,
                    producto.descripcion,
                    str(producto.precio),
                    producto.iva_pct,
                    producto.estado.value,
                    producto.codigo,
                ),
            )
        if cursor.rowcount == 0:
            raise LookupError(f"No existe el producto {producto.codigo}")

    def listar(self) -> list[Producto]:
        filas = self._conexion.execute("SELECT * FROM productos ORDER BY codigo").fetchall()
        return [self._desde_fila(fila) for fila in filas]

    def eliminar(self, codigo: str) -> None:
        with self._conexion:
            cursor = self._conexion.execute(
                "DELETE FROM productos WHERE codigo = ?", (codigo.strip().upper(),)
            )
        if cursor.rowcount == 0:
            raise LookupError(f"No existe el producto {codigo.strip().upper()}")

    @staticmethod
    def _desde_fila(fila: sqlite3.Row) -> Producto:
        return Producto(
            codigo=fila["codigo"],
            nombre=fila["nombre"],
            descripcion=fila["descripcion"],
            precio=fila["precio"],
            iva_pct=fila["iva_pct"],
            estado=fila["estado"],
        )


class RegistroClientesSQLite(_BaseSQLite):
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

    def buscar_coincidencias(self, termino: str) -> list[Cliente]:
        clave = termino.strip()
        if not clave:
            return []
        filas = self._conexion.execute(
            """
            SELECT * FROM clientes
            WHERE identificacion LIKE ? OR LOWER(nombre) LIKE ?
            ORDER BY identificacion
            """,
            (f"{clave}%", f"%{clave.lower()}%"),
        ).fetchall()
        return [self._desde_fila(fila) for fila in filas]

    def actualizar(self, cliente: Cliente) -> None:
        with self._conexion:
            cursor = self._conexion.execute(
                """
                UPDATE clientes
                SET nombre = ?, direccion = ?, telefono = ?, email = ?, tipo = ?, estado = ?
                WHERE identificacion = ?
                """,
                (
                    cliente.nombre,
                    cliente.direccion,
                    cliente.telefono,
                    str(cliente.email),
                    cliente.tipo.value,
                    cliente.estado.value,
                    str(cliente.identificacion),
                ),
            )
        if cursor.rowcount == 0:
            raise LookupError(f"No existe el cliente {cliente.identificacion}")

    def listar(self) -> list[Cliente]:
        filas = self._conexion.execute("SELECT * FROM clientes ORDER BY identificacion").fetchall()
        return [self._desde_fila(fila) for fila in filas]

    def eliminar(self, identificacion: RUC | str) -> None:
        clave = str(identificacion).strip()
        try:
            with self._conexion:
                cursor = self._conexion.execute(
                    "DELETE FROM clientes WHERE identificacion = ?", (clave,)
                )
        except sqlite3.IntegrityError as error:
            raise ValueError(
                "No se puede eliminar el cliente porque tiene proformas asociadas"
            ) from error
        if cursor.rowcount == 0:
            raise LookupError(f"No existe el cliente {clave}")

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
