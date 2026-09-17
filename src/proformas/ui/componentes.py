"""Componentes visuales compartidos por las vistas Flet."""

import flet as ft
from pydantic import ValidationError


def seccion(titulo: str, contenido: ft.Control) -> ft.Card:
    return ft.Card(
        ft.Container(
            ft.Column([ft.Text(titulo, size=16, weight=ft.FontWeight.W_600), contenido]),
            padding=18,
        )
    )


def total(etiqueta: str, valor: float, destacado: bool = False) -> ft.Row:
    peso = ft.FontWeight.BOLD if destacado else ft.FontWeight.NORMAL
    return ft.Row(
        [ft.Text(etiqueta, weight=peso), ft.Text(f"${valor:,.2f}", weight=peso)],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )


def mostrar_error(page: ft.Page, mensaje: str) -> None:
    page.show_dialog(
        ft.AlertDialog(
            title=ft.Text("Revisa la información"),
            content=ft.Text(mensaje),
            actions=[ft.FilledButton("Aceptar", on_click=lambda _: page.pop_dialog())],
        )
    )


def mensaje_error(error: Exception) -> str:
    if isinstance(error, ValidationError):
        return str(error.errors()[0]["msg"])
    return str(error)
