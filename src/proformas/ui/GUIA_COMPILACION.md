# Guía de Compilación y Generación de Ejecutables Multiplataforma

Este documento detalla el procedimiento formal para empaquetar y generar ejecutables independientes del **Sistema de Gestión de Proformas** en entornos **Linux**, **macOS** y **Windows**.

---

## 1. Fundamentos Técnicos del Empaquetado

La aplicación está construida sobre **Python** y la interfaz gráfica **Flet**, la cual se apoya internamente en el motor de **Flutter**.

Debido a la inclusión de bibliotecas binarias compiladas en C/C++ y componentes nativos de cada sistema operativo:
* **No es viable la compilación cruzada directa** de todos los sistemas desde un único entorno.
* **El binario para Linux** debe construirse en un entorno Linux (como Fedora).
* **El binario para macOS** (arquitectura ARM64 para procesadores Apple Silicon) debe construirse en un entorno macOS con sus respectivas herramientas de firma y desarrollo.
* **El ejecutable para Windows (`.exe`)** debe generarse en un entorno Windows o delegarse a un servicio de integración continua (CI/CD).

---

## 2. Métodos Disponibles en Flet

Usted dispone de dos alternativas principales según sus requerimientos:

| Enfoque | Comando base | Descripción | Recomendación |
| :--- | :--- | :--- | :--- |
| **Opción A: `flet pack`** | `uv run flet pack main.py` | Utiliza **PyInstaller** empaquetando el código Python junto con los binarios de Flet. | Recomendado para una generación rápida sin necesidad de instalar el SDK completo de Flutter. |
| **Opción B: `flet build`** | `uv run flet build <plataforma>` | Compila el host nativo de Flutter e incrusta el runtime de Python. | Recomendado para distribución de producción con integración nativa profunda. |

---

## 3. Generación en GNU/Linux (Fedora KDE)

Para generar el binario en su estación de trabajo con Fedora:

### 3.1. Método mediante `flet pack` (Recomendado)

1. Incorpore la dependencia de desarrollo `pyinstaller` si aún no está presente en su entorno:
   ```bash
   uv add --dev pyinstaller
   ```

2. Ejecute la orden de empaquetado:
   ```bash
   uv run flet pack main.py --name proformas
   ```

3. El ejecutable autocontenido se generará en el directorio `dist/proformas`.

### 3.2. Método mediante `flet build linux`

1. Instale previamente las dependencias de desarrollo requeridas por Flutter en Fedora:
   ```bash
   sudo dnf install clang cmake ninja-build gtk3-devel pkg-config
   ```

2. Inicie el proceso de compilación:
   ```bash
   uv run flet build linux
   ```
   *Nota: Si el SDK de Flutter no está instalado en su sistema, la herramienta le solicitará confirmación para descargarlo e instalarlo de manera asistida.*

3. El resultado compilado quedará disponible en el directorio `build/linux`.

---

## 4. Generación en macOS con Procesador ARM (Apple Silicon)

Para compilar en su equipo Mac con procesador ARM (M1, M2, M3 o M4):

### 4.1. Preparación del Entorno

1. Verifique que dispone de las herramientas de línea de comandos de Xcode:
   ```bash
   xcode-select --install
   ```

2. Clone o copie el proyecto en su equipo Mac y sincronice el entorno virtual:
   ```bash
   uv sync
   ```

### 4.2. Compilación

* **Opción con `flet pack`:**
  ```bash
  uv run flet pack main.py --name "Sistema de Proformas"
  ```
  Esto generará un paquete de aplicación nativo (`.app`) adaptado a la arquitectura ARM64 en la ruta `dist/Sistema de Proformas.app`.

* **Opción con `flet build macos`:**
  ```bash
  uv run flet build macos
  ```
  Esto construirá la aplicación nativa en `build/macos`.

---

## 5. Generación para Microsoft Windows (`.exe`)

Si usted no cuenta con una estación de trabajo física con Windows en este momento, dispone de las siguientes opciones:

### 5.1. Ejecución en un entorno local con Windows (Físico o Virtual)
Abra una terminal (PowerShell o CMD) en la raíz del proyecto y ejecute:
```powershell
uv sync
uv add --dev pyinstaller
uv run flet pack main.py --name proformas
```
El archivo resultante será `dist\proformas.exe`.

### 5.2. Automatización mediante GitHub Actions (Recomendado para los 3 Sistemas)
Puede delegar la generación automática de los ejecutables para Linux, macOS y Windows a los servidores de GitHub Actions. Para ello, cree el archivo `.github/workflows/compilacion.yml` con el siguiente contenido:

```yaml
name: Compilación Multiplataforma

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  construir:
    name: Compilar en ${{ matrix.os }}
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        include:
          - os: ubuntu-latest
            nombre_artefacto: proformas-linux
            comando: uv run flet pack main.py --name proformas
            ruta_salida: dist/proformas
          - os: macos-latest
            nombre_artefacto: proformas-macos-arm64
            comando: uv run flet pack main.py --name "Sistema de Proformas"
            ruta_salida: dist/Sistema de Proformas.app
          - os: windows-latest
            nombre_artefacto: proformas-windows
            comando: uv run flet pack main.py --name proformas
            ruta_salida: dist/proformas.exe

    steps:
      - name: Descargar código fuente
        uses: actions/checkout@v4

      - name: Instalar gestor uv
        uses: astral-sh/setup-uv@v5

      - name: Configurar versión de Python
        run: uv python install 3.12

      - name: Instalar dependencias del proyecto
        run: |
          uv sync
          uv add --dev pyinstaller

      - name: Compilar ejecutable
        run: ${{ matrix.comando }}

      - name: Publicar artefacto generado
        uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.nombre_artefacto }}
          path: ${{ matrix.ruta_salida }}
```

Cada vez que usted publique una etiqueta de versión (ejemplo: `v0.6.0`) o ejecute el flujo manualmente, GitHub Actions construirá los binarios nativos para cada arquitectura y sistema operativo.

---

## 6. Consideración Crítica sobre la Persistencia de Datos

En la implementación actual, la base de datos se inicializa por omisión mediante una ruta relativa:
```python
ruta_bd: str | Path = "data/proformas.db"
```

> [!WARNING]
> Tenga en cuenta que al ejecutar una aplicación compilada e instalada en directorios protegidos por el sistema operativo (tales como `/usr/bin/` en Linux, `/Applications/` en macOS o `C:\Program Files\` en Windows), el proceso no dispondrá de permisos de escritura en la ruta de instalación.
>
> Para despliegues en producción de escritorio, es altamente recomendable que usted configure la base de datos en una ubicación perteneciente al perfil del usuario, por ejemplo utilizando:
> ```python
> from pathlib import Path
> ruta_bd = Path.home() / ".proformas" / "proformas.db"
> ```
