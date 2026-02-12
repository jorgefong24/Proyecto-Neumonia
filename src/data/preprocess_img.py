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
    Preprocesa una imagen para el modelo de clasificación de neumonía.

    Realiza resize a 512x512, convierte a escala de grises, aplica CLAHE,
    normaliza valores a [0, 1] y expande dimensiones para batch.

    Args:
        array: Imagen en formato numpy (H, W) o (H, W, C).

    Returns:
        np.ndarray: Tensor preprocesado con forma (1, 512, 512, 1)
            y tipo float32.
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
