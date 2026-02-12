# Cómo ejecutar el proyecto

## Archivo a ejecutar

**`detector_neumonia.py`** — Es el punto de entrada. Abre la ventana de la herramienta de detección de neumonía.

**Atajo:** Puedes usar **`run.bat`** (doble clic o desde terminal): intenta usar el entorno virtual ya instalado y lanza la aplicación.

---

## Opción 1: Entorno virtual con pip (recomendada)

Abre una terminal en la carpeta **`UAO-Neumonia`** y ejecuta:

```powershell
# Ir a la carpeta del proyecto
cd "ruta\a\Proyecto Neumonia\UAO-Neumonia"

# Crear entorno virtual CON pip (si .venv no tiene pip, bórralo y crea de nuevo)
python -m venv .venv

# Activar entorno (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Si PowerShell da error de ejecución, ejecuta antes:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el proyecto
set TF_CPP_MIN_LOG_LEVEL=2
uv run python -m src.models.detector_neumonia
```

**Sin activar el venv** (usando el Python del venv directamente):

```powershell
cd "ruta\a\Proyecto Neumonia\UAO-Neumonia"
.\.venv\Scripts\pip.exe install -r requirements.txt
.\.venv\Scripts\python.exe detector_neumonia.py
```

---

## Opción 2: Con uv (si ya usas uv)

Desde la carpeta **`UAO-Neumonia`**:

```bash
pip install -r requirements.txt
uv run python -m src.models.detector_neumonia
```

O, si todas las dependencias están en `pyproject.toml`:

```bash
uv run python detector_neumonia.py
```

---

## Requisitos previos

1. **Python 3.10+** (el proyecto usa `>=3.10` en pyproject.toml).
2. **Modelo** `conv_MLP_84.h5`: debe estar en `UAO-Neumonia` o en la carpeta padre `Proyecto Neumonia` (ya está en la raíz del proyecto).
3. Imágenes de prueba en `Proyecto Neumonia/DICOM` o `Proyecto Neumonia/JPG`.

---

## Resumen rápido (Windows PowerShell)

```powershell
cd "c:\Users\Jorge\OneDrive\Documents\Especializacion en inteligencia artificial\Desarrollo de proyectos inteligencia artificial\Proyecto Neumonia\UAO-Neumonia"
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python detector_neumonia.py
```

Si no tienes aún el `.venv`, antes de activar ejecuta: `python -m venv .venv`.

---

## Si la instalación falla por "long path" (rutas largas) en Windows

El mensaje suele ser: `No such file or directory` en una ruta muy larga dentro de `.venv_run\Lib\site-packages\...`.

**Solución 1 – Activar soporte de rutas largas (recomendado):**

1. Abre PowerShell **como Administrador**.
2. Ejecuta:
   ```powershell
   New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
   ```
3. Reinicia el PC (o al menos cierra y vuelve a abrir la terminal).
4. Vuelve a la carpeta `UAO-Neumonia` y repite:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\pip install -r requirements.txt
   .\.venv\Scripts\python.exe detector_neumonia.py
   ```

**Solución 2 – Usar una ruta corta:**

Copia la carpeta del proyecto a una ruta corta, por ejemplo `C:\Neumonia`, y ejecuta allí los mismos comandos (crear venv, pip install, python detector_neumonia.py).
