# Cambios realizados y versiones de librerías

Este documento describe todo lo que se corrigió o configuró en el proyecto para que funcione correctamente, y las versiones de las librerías instaladas en el entorno .venv

Resumen de lo que se hizo

- Se creó un único entorno nuevo (`.venv`) con Python 3.10.
- Se instalaron todas las dependencias desde `requirements.txt`.
- Se ajustaron versiones de TensorFlow/Keras por compatibilidad.
- Se corrigieron errores en el código (imports, Grad-CAM, tkinter).

## Correcciones realizadas

Entornos virtuales

| Acción | Detalle |
| **Creado** | `.venv/` con Python 3.10 (único entorno del proyecto) |
| **Instalación** | Dependencias con `pip install -r requirements.txt` |

## TensorFlow y Keras

- En un primer momento se instaló **TensorFlow 2.20** con **Keras 3.12**, lo que rompía el código:
  - No existía `tensorflow.keras` como antes, lo que hacia que apareciera`ModuleNotFoundError: No module named 'tensorflow.python.trackable.data_structures'`. Lo que se hizo fue desinstalar TensorFlow 2.20 y Keras 3.x y se instaló TensorFlow 2.15.1 con Keras 2.15.0, compatibles con el código actual.

## Imports de Keras en el código

El proyecto usaba el paquete `keras` por separado. Se unificó el uso a `tensorflow.keras` para evitar conflictos:

| Archivo | Cambio |
|---------|--------|
| `detector_neumonia.py` | `import keras.backend as K` → `from tensorflow.keras import backend as K` |
| `grad_cam.py` | `import keras.layers as layers` → `from tensorflow.keras import layers` |

### Error en tkinter

- **Error:** `ImportError: cannot import name 'WARNING' from 'tkinter'`
- **Causa:** `WARNING` no existe en `tkinter`; el icono de advertencia está en `messagebox`.
- **Solución en `detector_neumonia.py`:**
  - Se quitó `WARNING` del import de `tkinter`.
  - Donde se usaba `icon=WARNING` en `messagebox.askokcancel`, se cambió a `icon=messagebox.WARNING`.

### Error en Grad-CAM

- **Error:** Al pulsar "Predecir", aparecía:  
  `ValueError: Attempt to convert a value (None) with an unsupported type (<class 'NoneType'>) to a Tensor` en `grad_cam.py` línea 111 (`tf.reduce_mean(grads, ...)`).
- **Causa:** Se usaban dos modelos separados (uno hasta la capa conv y otro hasta la salida). `class_channel` y `conv_output` no compartían grafo de cálculo, así que `tape.gradient(class_channel, conv_output)` devolvía `None`.
- **Solución en `grad_cam.py`:**
  - Se reemplazó el uso de `conv_model` y `pred_model` por un **único modelo con dos salidas**: `[last_conv.output, model.output]`.
  - En el `GradientTape` se hace una sola pasada: `conv_output, preds = two_output_model(batch_tensor)`, de modo que el gradiente de `class_channel` respecto a `conv_output` queda bien definido.
  - Se añadió una comprobación por si `grads` fuera `None`, con un mensaje de error claro.

### Scripts y documentación

- **run.bat:** Se dejó que use solo el entorno `.venv` (se quitó la lógica de `.venv_run`).
- **COMO_EJECUTAR.md:** Se actualizaron las instrucciones para usar `.venv` y Python 3.10+.

---

## Versiones de las librerías instaladas

Entorno: **.venv** (Python 3.10). Generado con `pip list --format=freeze`.

## Librerías principales del proyecto

| Librería | Versión | Uso en el proyecto |
|----------|---------|--------------------|
| **tensorflow** | 2.15.1 | Modelo de red neuronal, predicción |
| **keras** | 2.15.0 | API de modelo (tf.keras) |
| **numpy** | 1.26.4 | Arrays, preprocesado de imágenes |
| **pillow** | 12.1.0 | Imágenes (PIL), redimensionado |
| **pydicom** | 3.0.1 | Lectura de archivos DICOM |
| **opencv-python** | 4.13.0.92 | Procesamiento de imagen, Grad-CAM (heatmap) |
| **matplotlib** | 3.10.8 | Gráficos (si se usan) |
| **pandas** | 2.3.3 | Datos (si se usan) |
| **PyAutoGUI** | 0.9.54 | Automatización de ventanas |
| **tkcap** | 0.0.4 | Captura de ventanas Tkinter |
| **img2pdf** | 0.6.3 | Generación de PDF desde imágenes |
| **pytest** | 9.0.2 | Tests |

### Dependencias de TensorFlow (principales)

| Librería | Versión |
|----------|---------|
| tensorflow-intel | 2.15.1 |
| tensorboard | 2.15.2 |
| tensorflow-estimator | 2.15.0 |
| h5py | 3.15.1 |
| protobuf | 4.25.8 |
| grpcio | 1.78.0 |
| gast | 0.7.0 |
| absl-py | 2.4.0 |
| flatbuffers | 25.12.19 |
| ml-dtypes | 0.3.2 |
| opt-einsum | 3.4.0 |
| libclang | 18.1.1 |

### Otras dependencias instaladas

| Librería | Versión |
|----------|---------|
| certifi | 2026.1.4 |
| cffi | 2.0.0 |
| charset-normalizer | 3.4.4 |
| colorama | 0.4.6 |
| contourpy | 1.3.2 |
| cryptography | 46.0.4 |
| cycler | 0.12.1 |
| Deprecated | 1.3.1 |
| exceptiongroup | 1.3.1 |
| fonttools | 4.61.1 |
| google-auth | 2.48.0 |
| google-auth-oauthlib | 1.2.4 |
| google-pasta | 0.2.0 |
| idna | 3.11 |
| iniconfig | 2.3.0 |
| kiwisolver | 1.4.9 |
| lxml | 6.0.2 |
| Markdown | 3.10.1 |
| markdown-it-py | 4.0.0 |
| MarkupSafe | 3.0.3 |
| mdurl | 0.1.2 |
| MouseInfo | 0.1.3 |
| namex | 0.1.0 |
| oauthlib | 3.3.1 |
| optree | 0.18.0 |
| packaging | 26.0 |
| pikepdf | 10.3.0 |
| pluggy | 1.6.0 |
| pyasn1 | 0.6.2 |
| pyasn1_modules | 0.4.2 |
| pycparser | 3.0 |
| PyGetWindow | 0.0.9 |
| Pygments | 2.19.2 |
| PyMsgBox | 2.0.1 |
| pyparsing | 3.3.2 |
| pyperclip | 1.11.0 |
| PyRect | 0.2.0 |
| PyScreeze | 1.0.1 |
| python-dateutil | 2.9.0.post0 |
| pytweening | 1.2.0 |
| pytz | 2025.2 |
| requests | 2.32.5 |
| requests-oauthlib | 2.0.0 |
| rich | 14.3.2 |
| rsa | 4.9.1 |
| setuptools | 57.4.0 |
| six | 1.17.0 |
| tensorboard-data-server | 0.7.2 |
| tensorflow-io-gcs-filesystem | 0.31.0 |
| termcolor | 3.3.0 |
| tomli | 2.4.0 |
| typing_extensions | 4.15.0 |
| tzdata | 2025.3 |
| urllib3 | 2.6.3 |
| Werkzeug | 3.1.5 |
| wheel | 0.46.3 |
| wrapt | 1.14.2 |

### Cómo volver a generar esta lista

Desde la carpeta del proyecto, con el entorno activado:

```powershell
.\.venv\Scripts\Activate.ps1
pip list --format=freeze > versiones_instaladas.txt
```

O solo las que están en `requirements.txt`:

```powershell
pip list
```

---

## Cómo ejecutar el proyecto

```powershell
cd "c:\Users\Jorge\OneDrive\Desktop\Proyecto Neumonia\UAO-Neumonia"
.\.venv\Scripts\Activate.ps1
python detector_neumonia.py 
```

O doble clic en **run.bat**.

---

## Pruebas unitarias

El proyecto incluye pruebas unitarias en la carpeta **`tests/`**, usando **pytest** (versión 9.0.2).

### Pruebas disponibles

| Archivo | Pruebas | Qué comprueban |
|---------|---------|----------------|
| **tests/test_preprocess_img.py** | `test_preprocess_output_shape` | Que `preprocess()` devuelve un array de forma `(1, 512, 512, 1)`. |
| | `test_preprocess_output_dtype_and_range` | Que la salida es `float32` y los valores están en [0, 1]. |
| **tests/test_read_img.py** | `test_read_image_nonexistent_path_raises` | Que `read_image()` lanza `FileNotFoundError` si la ruta no existe. |
| | `test_read_jpg_file_nonexistent_path_raises` | Que `read_jpg_file()` lanza `FileNotFoundError` si la ruta no existe. |

**Total: 4 pruebas.** Todas pasan con el código actual.

### 5.2 Cómo ejecutar las pruebas

Desde la carpeta del proyecto, con el entorno activado:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest tests\ -v
```

Sin activar el entorno:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\ -v
```

Otras opciones útiles:

- `pytest tests\ -v` — modo verbose (más detalle).
- `pytest tests\ -v --tb=short` — trazas de error más cortas.
- `pytest tests\test_preprocess_img.py -v` — solo pruebas de preprocess.

### Resultado actual

```
tests/test_preprocess_img.py::test_preprocess_output_shape PASSED
tests/test_preprocess_img.py::test_preprocess_output_dtype_and_range PASSED
tests/test_read_img.py::test_read_image_nonexistent_path_raises PASSED
tests/test_read_img.py::test_read_jpg_file_nonexistent_path_raises PASSED