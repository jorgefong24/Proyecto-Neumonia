#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Módulo de carga del modelo de red neuronal para clasificación de neumonía.

Responsabilidad: cargar el archivo .h5 y validar integridad básica.
"""

import os
from typing import Iterable

from tensorflow import keras

MODEL_FILENAME = "conv_MLP_84.h5"
# También buscar alternativa entregada en el enunciado del curso
ALTERNATIVE_MODEL_FILENAMES = ("WilhemNet86.h5", "conv_MLP_84.h5")
_MODEL_CACHE = None


def _candidate_variants(candidate: str) -> Iterable[str]:
    """
    Devuelve variantes razonables para buscar el modelo.

    Si llega una ruta absoluta que no existe (por ejemplo /data/modelo.h5),
    también intenta con su nombre base para permitir buscar en otros montajes.
    """
    yield candidate
    basename = os.path.basename(candidate)
    if basename and basename != candidate:
        yield basename


def _search_dirs() -> list[str]:
    """Construye directorios de búsqueda en orden de prioridad."""
    module_dir = os.path.dirname(__file__)
    app_root = os.path.normpath(os.path.join(module_dir, "..", ".."))
    return [
        os.getcwd(),
        module_dir,
        os.path.normpath(os.path.join(module_dir, "..")),
        app_root,
        "/project",
        "/data",
        "/app",
    ]


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

    # Buscar en la ruta proporcionada y luego en rutas de respaldo.
    found_path = None
    inspected_paths = []
    search_dirs = _search_dirs()
    for candidate in candidates:
        seen = set()
        for variant in _candidate_variants(candidate):
            # 1) intentar directo (absoluto o relativo al cwd)
            direct_path = os.path.abspath(variant)
            if direct_path not in seen:
                seen.add(direct_path)
                inspected_paths.append(direct_path)
                if os.path.isfile(direct_path):
                    found_path = direct_path
                    break

            # 2) intentar combinando con directorios de búsqueda
            for base_dir in search_dirs:
                combined = os.path.abspath(os.path.join(base_dir, variant))
                if combined in seen:
                    continue
                seen.add(combined)
                inspected_paths.append(combined)
                if os.path.isfile(combined):
                    found_path = combined
                    break
            if found_path is not None:
                break
        if found_path is not None:
            break

    if found_path is None:
        unique_paths = list(dict.fromkeys(inspected_paths))
        raise FileNotFoundError(
            "No se encontró ningún modelo. "
            f"Candidatos de entrada: {candidates}. "
            f"Rutas inspeccionadas: {unique_paths}"
        )

    if _MODEL_CACHE is not None:
        return _MODEL_CACHE

    model = keras.models.load_model(found_path, compile=False)
    _MODEL_CACHE = model
    return model


def clear_model_cache():
    """Limpia la caché del modelo cargado (útil para tests o recarga)."""
    global _MODEL_CACHE
    _MODEL_CACHE = None
