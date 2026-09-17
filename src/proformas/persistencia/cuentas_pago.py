"""Persistencia de cuentas e instrucciones de pago reutilizables."""

import sqlite3
from pathlib import Path

from proformas.dominio import CuentaPago


class RepositorioCuentasPagoSQLite:
    def __init__(self, ruta_bd: str | Path) -> None:
        self._conexion = sqlite3.connect(str(ruta_bd))
        self._conexion.row_factory = sqlite3.Row
        self._conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS cuentas_pago (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                instrucciones TEXT NOT NULL
            )
            """
        )
        self._conexion.commit()

    def registrar(self, cuenta: CuentaPago) -> CuentaPago:
        try:
            with self._conexion:
                cursor = self._conexion.execute(
                    "INSERT INTO cuentas_pago (nombre, instrucciones) VALUES (?, ?)",
                    (cuenta.nombre, cuenta.instrucciones),
                )
        except sqlite3.IntegrityError as error:
            raise ValueError(f"Ya existe una cuenta de pago llamada {cuenta.nombre}") from error
        return cuenta.model_copy(update={"id": cursor.lastrowid})

    def listar(self) -> list[CuentaPago]:
        filas = self._conexion.execute(
            "SELECT id, nombre, instrucciones FROM cuentas_pago ORDER BY nombre"
        ).fetchall()
        return [CuentaPago(**dict(fila)) for fila in filas]

    def eliminar(self, cuenta_id: int) -> None:
        with self._conexion:
            cursor = self._conexion.execute("DELETE FROM cuentas_pago WHERE id = ?", (cuenta_id,))
        if cursor.rowcount == 0:
            raise LookupError("No existe la cuenta de pago seleccionada")
