"""Menú interactivo de consola con entrada y salida inyectables."""

from collections.abc import Callable

from pydantic import ValidationError

from proformas.aplicacion import AplicacionProformas
from proformas.modelo import AtributosFisicos, Cliente, Producto, Talla, TipoCliente
from proformas.presentacion.formateadores import (
    formatear_cliente,
    formatear_detalle_proforma,
    formatear_producto,
)

Entrada = Callable[[str], str]
Salida = Callable[[str], None]

_TIPOS_CLIENTE = {
    "1": TipoCliente.PUBLICO,
    "2": TipoCliente.MAYORISTA,
    "3": TipoCliente.MEDICO,
}

_TALLAS = {t.value: t for t in Talla}


class MenuConsola:
    OPCIONES = """
Sistema de Gestión de Proformas - Fase 4
1. Registrar producto
2. Listar productos
3. Dar de baja un producto
4. Registrar cliente
5. Listar clientes
6. Dar de baja un cliente
7. Mostrar proforma demo
0. Salir
""".strip()

    def __init__(
        self,
        aplicacion: AplicacionProformas,
        entrada: Entrada = input,
        salida: Salida = print,
    ) -> None:
        self.aplicacion = aplicacion
        self.entrada = entrada
        self.salida = salida
        self._acciones: dict[str, Callable[[], None]] = {
            "1": self._registrar_producto,
            "2": self._listar_productos,
            "3": self._dar_baja_producto,
            "4": self._registrar_cliente,
            "5": self._listar_clientes,
            "6": self._dar_baja_cliente,
            "7": self._mostrar_proforma,
        }

    def ejecutar(self) -> None:
        while True:
            self.salida(self.OPCIONES)
            try:
                opcion = self.entrada("Seleccione una opción: ").strip()
            except (EOFError, KeyboardInterrupt):
                self.salida("Sesión finalizada.")
                return

            if opcion == "0":
                self.salida("Hasta pronto.")
                return

            accion = self._acciones.get(opcion)
            if accion is None:
                self.salida("Opción no válida.")
                continue

            try:
                accion()
            except (ValidationError, ValueError, LookupError) as error:
                self.salida(f"Error: {self._mensaje_error(error)}")

    def _registrar_producto(self) -> None:
        codigo = self.entrada("Código: ")
        nombre = self.entrada("Nombre: ")
        precio = self.entrada("Precio: ")
        iva = self.entrada("IVA % (Enter = 15): ") or "15"

        # Atributos físicos opcionales
        peso_texto = self.entrada("Peso en kg (Enter = omitir): ").strip()
        extras = None
        if peso_texto:
            talla_texto = self.entrada(
                f"Talla ({', '.join(t.value for t in Talla)}) (Enter = omitir): "
            ).strip()
            talla = _TALLAS.get(talla_texto)
            extras = AtributosFisicos(peso_kg=float(peso_texto), talla=talla)

        producto = Producto(
            codigo=codigo,
            nombre=nombre,
            precio=precio,
            iva_pct=iva,
            extras=extras,
        )
        self.aplicacion.registrar_producto(producto)
        self.salida("Producto registrado.")

    def _listar_productos(self) -> None:
        productos = self.aplicacion.listar_productos()
        self.salida("\n".join(map(formatear_producto, productos)) or "No hay productos.")

    def _dar_baja_producto(self) -> None:
        producto = self.aplicacion.dar_baja_producto(self.entrada("Código: "))
        self.salida(f"Producto dado de baja: {producto.nombre}.")

    def _registrar_cliente(self) -> None:
        self.salida("Tipo de cliente: 1=Público  2=Mayorista  3=Médico")
        tipo_texto = self.entrada("Tipo (Enter = Público): ").strip() or "1"
        tipo = _TIPOS_CLIENTE.get(tipo_texto, TipoCliente.PUBLICO)

        cliente = Cliente(
            identificacion=self.entrada("Cédula o RUC: "),
            nombre=self.entrada("Nombre: "),
            email=self.entrada("Email (opcional): "),
            tipo=tipo,
        )
        self.aplicacion.registrar_cliente(cliente)
        self.salida("Cliente registrado.")

    def _listar_clientes(self) -> None:
        clientes = self.aplicacion.listar_clientes()
        self.salida("\n".join(map(formatear_cliente, clientes)) or "No hay clientes.")

    def _dar_baja_cliente(self) -> None:
        cliente = self.aplicacion.dar_baja_cliente(self.entrada("Cédula o RUC: "))
        self.salida(f"Cliente dado de baja: {cliente.nombre}.")

    def _mostrar_proforma(self) -> None:
        self.salida(formatear_detalle_proforma(self.aplicacion.crear_proforma_demo()))

    @staticmethod
    def _mensaje_error(error: Exception) -> str:
        if isinstance(error, ValidationError):
            return str(error.errors()[0]["msg"])
        return str(error)
