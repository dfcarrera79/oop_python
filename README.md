# Sistema de Gestión de Proformas

Sistema educativo de gestión de proformas desarrollado en Python con persistencia en **SQLite**, interfaz gráfica de escritorio en **Flet** y exportación de documentos a **PDF** mediante ReportLab.

---

## Requisitos previos

* **Python 3.12** o superior.
* Gestor de paquetes y entornos [**uv**](https://docs.astral.sh/uv/):
  ```bash
  # En Linux / macOS
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # En Windows (PowerShell)
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

---

## Instalación y preparación

1. Clona el repositorio y sitúate en el directorio del proyecto:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd oop_python
   ```
   *(Opcional: Si deseas cambiar a una rama específica, puedes usar `git checkout semana6` o `git checkout main`).*

2. Sincroniza e instala las dependencias del proyecto de manera automática con `uv`:
   ```bash
   uv sync
   ```

---

## Cómo ejecutar la aplicación

Para iniciar la aplicación con interfaz gráfica de escritorio:

```bash
uv run main.py
```

> **Nota:** La primera vez que se ejecuta, Flet descargará y configurará automáticamente el motor de ejecución de escritorio (`flet-desktop`).

---

## Estructura del proyecto

* `main.py`: Punto de entrada que inicializa la ventana y la interfaz de Flet.
* `src/proformas/`:
  * `dominio/`: Entidades de negocio, validaciones con Pydantic (`Cliente`, `Producto`, `Proforma`, valores y enums).
  * `persistencia/`: Repositorios SQLite (`CatalogoProductosSQLite`, `RegistroClientesSQLite`, `RepositorioProformasSQLite`).
  * `exportacion/`: Generación de proformas en formato PDF con ReportLab.
  * `ui/`: Vistas y componentes de la interfaz gráfica desarrollada en Flet.
* `data/proformas.db`: Base de datos SQLite local.

---

## Compilación y generación de ejecutables

Para empaquetar la aplicación como un ejecutable independiente (Linux, macOS o Windows):

```bash
# Instalar pyinstaller en el entorno de desarrollo
uv add --dev pyinstaller

# Generar el ejecutable autocontenido
uv run flet pack main.py --name proformas
```

Para instrucciones detalladas sobre compilación multiplataforma y flujos de CI/CD con GitHub Actions, consulta la [Guía de Compilación](src/proformas/ui/GUIA_COMPILACION.md).
