#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Módulo de carga del modelo de red neuronal para clasificación de neumonía.

Responsabilidad: cargar el archivo .h5 y validar integridad básica.
"""

import os

from tensorflow import keras

MODEL_FILENAME = "conv_MLP_84.h5"
_MODEL_CACHE = None


def load_model(path=None):
    
    global _MODEL_CACHE
    if path is None:
        path = MODEL_FILENAME
    if not os.path.isfile(path):
        # Fallback: buscar en directorio padre (proyecto raíz)
        parent_path = os.path.join(os.path.dirname(__file__), "..", MODEL_FILENAME)
        parent_path = os.path.normpath(parent_path)
        if os.path.isfile(parent_path):
            path = parent_path
        else:
            raise FileNotFoundError(f"No se encontró el modelo: {path}")
    if _MODEL_CACHE is not None:
        return _MODEL_CACHE
    model = keras.models.load_model(path, compile=False)
    _MODEL_CACHE = model
    return model


def clear_model_cache():
    """
    Limpia la caché del modelo cargado (útil para tests o recarga).
    """
    global _MODEL_CACHE
    _MODEL_CACHE = None
