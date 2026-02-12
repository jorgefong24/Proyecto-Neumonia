#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Módulo de carga del modelo de red neuronal para clasificación de neumonía.

Responsabilidad: cargar el archivo .h5 y validar integridad básica.
"""

import os

from tensorflow import keras

MODEL_FILENAME = "conv_MLP_84.h5"
# También buscar alternativa entregada en el enunciado del curso
ALTERNATIVE_MODEL_FILENAMES = ("WilhemNet86.h5", "conv_MLP_84.h5")
_MODEL_CACHE = None


def load_model(path=None):
    """
    Carga el modelo .h5. Si `path` es None intenta localizar uno de los
    nombres esperados en el directorio del proyecto.

    Args:
        path (str|None): Ruta al archivo .h5. Si es None, se buscan nombres
            comunes (ver `ALTERNATIVE_MODEL_FILENAMES`).

    Returns:
        keras.Model: Modelo cargado.

    Raises:
        FileNotFoundError: Si no se encuentra ningún archivo de modelo.
    """
    global _MODEL_CACHE
    candidates = []
    if path:
        candidates.append(path)
    else:
        # Priorizar el nombre por defecto y luego alternativas
        candidates.extend(ALTERNATIVE_MODEL_FILENAMES)

    # Buscar en la ruta proporcionada, luego en carpeta del módulo, luego
    # en el directorio padre del proyecto.
    found_path = None
    for candidate in candidates:
        if os.path.isabs(candidate) and os.path.isfile(candidate):
            found_path = candidate
            break
        # buscar relativo al cwd
        if os.path.isfile(candidate):
            found_path = os.path.abspath(candidate)
            break
        # buscar en la carpeta del módulo
        module_path = os.path.join(os.path.dirname(__file__), candidate)
        if os.path.isfile(module_path):
            found_path = os.path.normpath(module_path)
            break
        # buscar en la carpeta padre del repo
        parent_path = os.path.join(os.path.dirname(__file__), "..", candidate)
        parent_path = os.path.normpath(parent_path)
        if os.path.isfile(parent_path):
            found_path = parent_path
            break

    if found_path is None:
        raise FileNotFoundError(f"No se encontró ningún modelo entre: {candidates}")

    if _MODEL_CACHE is not None:
        return _MODEL_CACHE

    model = keras.models.load_model(found_path, compile=False)
    _MODEL_CACHE = model
    return model


def clear_model_cache():
    """
    Limpia la caché del modelo cargado (útil para tests o recarga).
    """
    global _MODEL_CACHE
    _MODEL_CACHE = None
