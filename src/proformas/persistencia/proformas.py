"""Persistencia transaccional de proformas e ítems en SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from proformas.dominio import Cliente, ItemProforma, Producto, Proforma, Talla, TipoCliente


class RepositorioProformasSQLite:
    """Conserva la cabecera y las líneas de cada proforma de forma atómica."""

    def __init__(self, ruta_bd: str | Path) -> None:
        self.ruta_bd = str(ruta_bd)
        Path(self.ruta_bd).parent.mkdir(parents=True, exist_ok=True)
        self._conexion = sqlite3.connect(self.ruta_bd)
        self._conexion.row_factory = sqlite3.Row
        self._conexion.execute("PRAGMA foreign_keys = ON")
        self._crear_esquema()

    def _crear_esquema(self) -> None:
        self._conexion.executescript(
            """
            CREATE TABLE IF NOT EXISTS proformas (
                numero TEXT PRIMARY KEY,
                fecha TEXT NOT NULL,
                cliente_identificacion TEXT NOT NULL,
                observaciones TEXT NOT NULL DEFAULT '',
                instrucciones_pago TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (cliente_identificacion) REFERENCES clientes(identificacion)
            );

            CREATE TABLE IF NOT EXISTS items_proforma (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proforma_numero TEXT NOT NULL,
                posicion INTEGER NOT NULL,
                producto_codigo TEXT NOT NULL,
                producto_nombre TEXT NOT NULL,
                producto_descripcion TEXT NOT NULL DEFAULT '',
                precio_unitario TEXT NOT NULL,
                iva_pct REAL NOT NULL,
                cantidad INTEGER NOT NULL CHECK (cantidad > 0),
                tipo_cliente TEXT,
                talla TEXT,
                UNIQUE (proforma_numero, posicion),
                FOREIGN KEY (proforma_numero) REFERENCES proformas(numero) ON DELETE CASCADE
            );
            """
        )
        columnas = {
            fila["name"]
            for fila in self._conexion.execute("PRAGMA table_info(items_proforma)").fetchall()
        }
        if "talla" not in columnas:
            self._conexion.execute("ALTER TABLE items_proforma ADD COLUMN talla TEXT")
        self._conexion.commit()

    def siguiente_numero(self) -> str:
        fila = self._conexion.execute(
            "SELECT numero FROM proformas WHERE numero LIKE 'PRO-%' ORDER BY numero DESC LIMIT 1"
        ).fetchone()
        siguiente = int(fila["numero"].removeprefix("PRO-")) + 1 if fila else 1
        return f"PRO-{siguiente:06d}"

    def guardar(self, proforma: Proforma) -> None:
        if not proforma.items:
            raise ValueError("La proforma debe contener al menos un producto")
        try:
            with self._conexion:
                self._conexion.execute(
                    """
                    INSERT INTO proformas
                    (numero, fecha, cliente_identificacion, observaciones, instrucciones_pago)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        proforma.numero,
                        proforma.fecha.isoformat(),
                        str(proforma.cliente.identificacion),
                        proforma.observaciones,
                        proforma.instrucciones_pago,
                    ),
                )
                self._conexion.executemany(
                    """
                    INSERT INTO items_proforma
                    (proforma_numero, posicion, producto_codigo, producto_nombre,
                     producto_descripcion, precio_unitario, iva_pct, cantidad, tipo_cliente, talla)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        self._item_a_fila(proforma.numero, posicion, item)
                        for posicion, item in enumerate(proforma.items, start=1)
                    ],
                )
        except sqlite3.IntegrityError as error:
            raise ValueError(f"No se pudo guardar la proforma {proforma.numero}") from error

    def buscar(self, numero: str) -> Proforma | None:
        cabecera = self._conexion.execute(
            """
            SELECT p.*, c.nombre, c.direccion, c.telefono, c.email, c.tipo, c.estado
            FROM proformas p
            JOIN clientes c ON c.identificacion = p.cliente_identificacion
            WHERE p.numero = ?
            """,
            (numero.strip(),),
        ).fetchone()
        return self._desde_cabecera(cabecera) if cabecera else None

    def listar(self) -> list[Proforma]:
        numeros = self._conexion.execute(
            "SELECT numero FROM proformas ORDER BY fecha DESC, numero DESC"
        ).fetchall()
        return [proforma for fila in numeros if (proforma := self.buscar(fila["numero"]))]

    def eliminar(self, numero: str) -> None:
        with self._conexion:
            cursor = self._conexion.execute(
                "DELETE FROM proformas WHERE numero = ?", (numero.strip(),)
            )
        if cursor.rowcount == 0:
            raise LookupError(f"No existe la proforma {numero.strip()}")

    def cerrar(self) -> None:
        self._conexion.close()

    @staticmethod
    def _item_a_fila(numero: str, posicion: int, item: ItemProforma) -> tuple[object, ...]:
        return (
            numero,
            posicion,
            item.producto.codigo,
            item.producto.nombre,
            item.producto.descripcion,
            str(item.producto.precio),
            item.producto.iva_pct,
            item.cantidad,
            item.tipo_cliente.value if item.tipo_cliente else None,
            item.talla.value if item.talla else None,
        )

    def _desde_cabecera(self, fila: sqlite3.Row) -> Proforma:
        cliente = Cliente(
            identificacion=fila["cliente_identificacion"],
            nombre=fila["nombre"],
            direccion=fila["direccion"],
            telefono=fila["telefono"],
            email=fila["email"],
            tipo=fila["tipo"],
            estado=fila["estado"],
        )
        filas_items = self._conexion.execute(
            "SELECT * FROM items_proforma WHERE proforma_numero = ? ORDER BY posicion",
            (fila["numero"],),
        ).fetchall()
        items = [
            ItemProforma(
                producto=Producto(
                    codigo=item["producto_codigo"],
                    nombre=item["producto_nombre"],
                    descripcion=item["producto_descripcion"],
                    precio=item["precio_unitario"],
                    iva_pct=item["iva_pct"],
                ),
                cantidad=item["cantidad"],
                tipo_cliente=TipoCliente(item["tipo_cliente"]) if item["tipo_cliente"] else None,
                talla=Talla(item["talla"]) if item["talla"] else None,
            )
            for item in filas_items
        ]
        return Proforma(
            numero=fila["numero"],
            fecha=fila["fecha"],
            cliente=cliente,
            items=items,
            observaciones=fila["observaciones"],
            instrucciones_pago=fila["instrucciones_pago"],
        )
