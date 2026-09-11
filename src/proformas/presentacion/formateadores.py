"""Transformaciones puras de objetos del dominio a texto."""

from proformas.modelo import AtributosFisicos, Cliente, Producto, Proforma


def formatear_producto(producto: Producto) -> str:
    partes = [
        f"[{producto.codigo}] {producto.nombre}",
        f"${producto.precio:.2f}",
        f"(IVA {producto.iva_pct:.1f}%)",
    ]
    if isinstance(producto.extras, AtributosFisicos):
        if producto.extras.talla is not None:
            partes.insert(2, f"Talla {producto.extras.talla.value}")
        partes.append(f"{producto.extras.peso_kg} kg")
    partes.append(producto.estado.value)
    return " - ".join(partes)


def formatear_cliente(cliente: Cliente) -> str:
    partes = [
        f"[{cliente.identificacion}] {cliente.nombre}",
        cliente.direccion,
        cliente.telefono,
        str(cliente.email),
        cliente.tipo.value,
        cliente.estado.value,
    ]
    return " - ".join(partes)


def formatear_proforma(proforma: Proforma) -> str:
    unidad = "ítem" if len(proforma.items) == 1 else "ítems"
    return (
        f"Proforma {proforma.numero} - {proforma.cliente.nombre} - "
        f"{len(proforma.items)} {unidad} - ${proforma.total():.2f}"
    )


def formatear_detalle_proforma(proforma: Proforma) -> str:
    lineas = [formatear_proforma(proforma)]
    lineas.extend(
        f"  {item.cantidad} x {item.producto.nombre}: ${item.total():.2f}"
        for item in proforma.items
    )
    lineas.extend(
        [
            f"Subtotal: ${proforma.subtotal():.2f}",
            f"IVA: ${proforma.impuesto():.2f}",
            f"Total: ${proforma.total():.2f}",
        ]
    )
    return "\n".join(lineas)
