# Los 7 errores identificados en el proyecto

## 1. **`dicom` no está importado**
- **Ubicación:** `read_dicom_file()` en `detector_neumonia.py` (línea ~71).
- **Problema:** Se usa `dicom.read_file(path)` pero no existe `import pydicom` ni ningún alias `dicom`. Esto provoca `NameError: name 'dicom' is not defined` al cargar un DICOM.
- **Además:** La API `pydicom.read_file()` está deprecada; debe usarse `pydicom.dcmread()`.

## 2. **`K` (backend de Keras) no está importado**
- **Ubicación:** Función `grad_cam()` (líneas 28-31).
- **Problema:** Se usan `K.gradients`, `K.mean` y `K.function` pero no se importa el backend de Keras (`from tensorflow.keras import backend as K`). Produce `NameError: name 'K' is not defined` al predecir.

## 3. **`model_fun()` no está definida**
- **Ubicación:** Llamadas en `grad_cam()` (línea 24) y `predict()` (línea 55).
- **Problema:** La función `model_fun()` no existe en el archivo. El modelo nunca se carga; la única referencia es un comentario que menciona `tf.keras.models.load_model('conv_MLP_84.h5')`. Al ejecutar "Predecir" se produce `NameError: name 'model_fun' is not defined`.

## 4. **Siempre se usa DICOM al cargar imagen**
- **Ubicación:** `load_img_file()` (línea ~196).
- **Problema:** Siempre se llama `read_dicom_file(filepath)` sin importar si el usuario eligió un archivo `.dcm`, `.jpeg`, `.jpg` o `.png`. Para JPEG/PNG falla porque `dicom.read_file()` no puede leer esos formatos.
- **Solución:** Detectar la extensión y usar `read_dicom_file()` para `.dcm` y `read_jpg_file()` para el resto.

## 5. **Uso de `Image.ANTIALIAS` deprecado**
- **Ubicación:** Líneas 201 y 205 en `load_img_file()` y `run_model()`.
- **Problema:** En Pillow 10+ `Image.ANTIALIAS` está deprecado. Debe usarse `Image.LANCZOS` o `Image.Resampling.LANCZOS` para mantener compatibilidad y evitar warnings.

## 6. **`requirements.txt` sin versiones**
- **Ubicación:** Archivo `requirements.txt`.
- **Problema:** El enunciado exige "agregar las versiones a las librerías utilizadas". El archivo actual solo lista nombres (pyautogui, pillow, tkcap, etc.) sin fijar versiones, lo que puede provocar incompatibilidades entre entornos.

## 7. **Modelo `.h5` no está en `.gitignore`**
- **Ubicación:** No existe `.gitignore` en el proyecto o no incluye `*.h5`.
- **Problema:** El enunciado indica que "El modelo .h5 se tiene que agregar al .gitignore". Sin esto, el modelo podría subirse al repositorio (pesado y a veces con restricciones de licencia).

---

**Resumen:** Los errores 1, 2 y 3 provocan fallos en tiempo de ejecución al usar DICOM o al predecir. Los errores 4, 5, 6 y 7 son de diseño, mantenibilidad y cumplimiento de requisitos.
