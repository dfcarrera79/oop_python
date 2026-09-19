# Guía de clase 7: TDA lineales, Repository y pruebas unitarias

Esta guía acompaña el código de `src/proformas/ejemplos_semana7.py`. Su propósito es construir una pila y una cola manualmente, ocultarlas detrás de repositorios y comprobar su comportamiento con `pytest`. También conecta estas pruebas con el dominio desarrollado hasta la semana 6.

## Objetivos

Al terminar la práctica podrás:

- Distinguir un TDA de su implementación concreta.
- Explicar y comprobar los órdenes LIFO y FIFO.
- Entender cómo Repository separa el acceso a los datos del resto del programa.
- Preparar datos con fixtures y verificar resultados y excepciones con `pytest`.

## Preparación y comandos

Instala las dependencias y ejecuta el ejemplo:

```bash
uv sync
uv run python -m proformas.ejemplos_semana7
```

Ejecuta todas las pruebas o solamente las de esta clase:

```bash
uv run pytest -v
uv run pytest tests/test_semana7.py -v
uv run pytest tests/test_dominio_semana6.py -v
```

## 1. Tipo de dato abstracto

Un TDA se define por las operaciones que ofrece y por las reglas de esas operaciones, no por el código usado para guardar los datos. Por ejemplo, una pila ofrece `apilar`, `desapilar` y `esta_vacia`. Puede implementarse con un arreglo, una lista enlazada u otro mecanismo sin cambiar la idea de pila.

En Python simulamos un arreglo fijo con:

```python
self._elementos = [None] * capacidad
```

`len(self._elementos)` representa la **capacidad física** y `_cantidad` representa cuántos elementos están almacenados. Confundirlos suele producir accesos fuera de rango.

## 2. Pila: orden LIFO

`Pila` coloca el nuevo objeto en `_elementos[_cantidad]` y luego incrementa el contador. Para retirarlo hace el proceso inverso: decrementa el contador, lee esa posición y la limpia con `None`.

```python
pila.apilar("primero")
pila.apilar("ultimo")
assert pila.desapilar() == "ultimo"
```

Esto demuestra LIFO: el último elemento en entrar es el primero en salir. Limpiar la posición evita conservar referencias a objetos que ya no pertenecen a la estructura.

Los intentos de apilar cuando no queda espacio o desapilar una pila vacía generan `IndexError`. Una excepción explícita comunica el error mejor que devolver `None`, pues `None` podría confundirse con un dato válido.

## 3. Cola circular: orden FIFO

La cola necesita `_frente` además de `_cantidad`. La posición de inserción se calcula así:

```python
posicion_final = (self._frente + self._cantidad) % len(self._elementos)
```

El operador `%` permite regresar al índice cero al alcanzar el final del arreglo. No se desplazan todos los elementos cada vez que alguien sale: solo avanza `_frente`. Esto mantiene constantes las operaciones de encolar y desencolar.

La prueba `test_cola_respeta_orden_fifo_y_reutiliza_espacio` llena la cola, retira a Ana y agrega a Marta. Esa última inserción obliga a reutilizar el índice cero y comprueba el caso circular que con frecuencia se olvida.

## 4. Patrón Repository

`RepositorioProductos` expone verbos relacionados con el problema: `agregar`, `retirar_ultimo` y `esta_vacio`. Quien lo usa no conoce `_elementos`, `_cantidad` ni siquiera necesita llamar a `apilar`.

```python
repositorio = RepositorioProductos(2)
repositorio.agregar(mouse)
producto = repositorio.retirar_ultimo()
```

`RepositorioAtencion` ofrece `atender_siguiente` y usa una cola. Elegir una pila para este caso atendería primero a la última persona y rompería la regla del negocio. El repositorio debe almacenar y recuperar; descuentos, impuestos u otras reglas comerciales pertenecen a servicios o entidades del dominio.

## 5. Anatomía de las pruebas de semana 7

### Fixture

```python
@pytest.fixture
def pila():
    return Pila(capacidad=2)
```

Pytest crea una pila nueva para cada prueba que solicite el parámetro `pila`. Así las pruebas no dependen de su orden ni comparten estado residual.

### Verificación directa

Una expresión `assert` documenta el resultado esperado. En `test_pila_respeta_orden_lifo`, los dos `assert` no son casos inconexos: juntos comprueban el orden completo de salida.

### Verificación de errores

```python
with pytest.raises(IndexError, match="vacia"):
    pila.desapilar()
```

La prueba pasa únicamente si se lanza `IndexError` y el mensaje contiene `vacia`. Esto verifica tanto el tipo de fallo como que sea comprensible.

### Identidad frente a igualdad

La prueba del repositorio usa `is` para demostrar que recupera exactamente la misma instancia de `Producto` agregada. `==` sería apropiado si solo importara que dos objetos tuvieran valores equivalentes.

## 6. Pruebas del código heredado de semana 6

La rama `semana6` ya incluye `pytest` en las dependencias, pero no contenía archivos de prueba versionados. `tests/test_dominio_semana6.py` agrega pruebas de regresión sobre el `Producto` real del proyecto:

- `test_producto_normaliza_codigo_y_precio` comprueba dos responsabilidades: el código se recorta y convierte a mayúsculas, mientras `Monto` redondea el precio a dos decimales.
- `test_producto_rechaza_codigo_vacio` verifica con `pytest.raises` que Pydantic convierta la regla del validador en un `ValidationError` visible para quien usa el modelo.
- `test_calcular_precio_sin_iva` comprueba que un precio de 115 con IVA del 15 % se normalice a 100.00. Se compara con `Decimal`, no con un `float`, para conservar precisión monetaria.

Estas son pruebas unitarias porque ejercitan funciones y modelos pequeños sin iniciar Flet, escribir en SQLite ni generar archivos PDF. Si dependieran de esos componentes serían pruebas de integración y requerirían una preparación diferente.

## 7. Secuencia sugerida para la clase

1. Ejecutar el ejemplo y predecir quién sale primero en cada estructura.
2. Construir `Pila` hasta completar el comportamiento LIFO.
3. Ejecutar solo las pruebas cuyo nombre contiene `pila`: `uv run pytest -k pila -v`.
4. Construir la cola sin módulo, observar el error al reutilizar espacio y después introducir `%`.
5. Encapsular ambas estructuras detrás de los repositorios.
6. Revisar las pruebas de semana 6 para conectar las técnicas nuevas con el proyecto existente.
7. Ejecutar la suite completa y confirmar que una modificación no rompe comportamientos previos.

## 8. Ejercicios

1. Agrega una operación `ver_tope` a `Pila` que no retire el elemento y escribe primero sus pruebas para pila vacía y no vacía.
2. Implementa `RepositorioClientes` sobre `RepositorioAtencion` y verifica que Ana sea atendida antes que Luis.
3. Escribe pruebas para una cola llena y para una cola vacía.
4. Cambia internamente `RepositorioProductos` para usar una cola y describe qué prueba falla y por qué. No cambies la interfaz pública durante el experimento.

## Errores que debes evitar

- Usar `list.pop`, `list.append`, `collections.deque` o `queue.Queue` en esta práctica: resolverían el ejercicio sin implementar el TDA.
- Exponer `_elementos` desde un getter: permitiría modificar la estructura sin respetar sus reglas.
- Omitir los casos vacío, lleno y vuelta circular.
- Compartir una instancia mutable entre pruebas.
- Colocar reglas de precios o descuentos dentro del repositorio.
