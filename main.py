"""Punto de entrada de la aplicación de proformas (Flet)."""

import flet as ft

from proformas.ui import construir_interfaz


def main() -> None:
    if hasattr(ft, "run"):
        ft.run(construir_interfaz)
    else:
        ft.app(target=construir_interfaz)


if __name__ == "__main__":
    main()
