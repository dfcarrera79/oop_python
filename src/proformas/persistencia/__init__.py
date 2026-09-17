"""Persistencia SQLite del sistema."""

from proformas.persistencia.proformas import RepositorioProformasSQLite
from proformas.persistencia.sqlite import CatalogoProductosSQLite, RegistroClientesSQLite

__all__ = [
    "CatalogoProductosSQLite",
    "RegistroClientesSQLite",
    "RepositorioCuentasPagoSQLite",
    "RepositorioProformasSQLite",
]
from proformas.persistencia.cuentas_pago import RepositorioCuentasPagoSQLite
