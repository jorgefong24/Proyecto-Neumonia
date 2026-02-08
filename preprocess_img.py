#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Módulo de preprocesamiento de imágenes para el modelo de neumonía.

Responsabilidad: resize 512x512, escala de grises, CLAHE,
normalización 0-1 y conversión a tensor (batch).
"""

import cv2
import numpy as np

TARGET_SIZE = (512, 512)
CLAHE_CLIP = 2.0
CLAHE_GRID = (4, 4)


def preprocess(array):
    """
    Preprocesa un arreglo de imagen para entrada al modelo.

    - Redimensiona a 512x512.
    - Convierte a escala de grises (si viene en color).
    - Aplica ecualización CLAHE.
    - Normaliza en [0, 1].
    - Convierte a formato batch (1, H, W, 1).

    Args:
        array: numpy array (H, W) o (H, W, C), uint8 o float.

    Returns:
        numpy array de forma (1, 512, 512, 1), float en [0, 1].
    """
    array = cv2.resize(array, TARGET_SIZE)
    if len(array.shape) == 3:
        array = cv2.cvtColor(array, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=CLAHE_CLIP, tileGridSize=CLAHE_GRID)
    array = clahe.apply(array)
    array = array / 255.0
    array = np.expand_dims(array, axis=-1)
    array = np.expand_dims(array, axis=0)
    return array.astype(np.float32)
