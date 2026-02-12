#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pruebas unitarias para el módulo preprocess_img.
"""

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from preprocess_img import TARGET_SIZE, preprocess


def test_preprocess_output_shape():
    """
    Verifica que preprocess devuelve un tensor de forma (1, 512, 512, 1).
    """
    # Imagen aleatoria 300x400 en escala de grises
    img = np.random.randint(0, 256, (300, 400), dtype=np.uint8)
    out = preprocess(img)
    assert out.shape == (1, TARGET_SIZE[1], TARGET_SIZE[0], 1)


def test_preprocess_output_dtype_and_range():
    """
    Verifica que la salida es float32 y los valores están en [0, 1].
    """
    img = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
    out = preprocess(img)
    assert out.dtype == np.float32
    assert out.min() >= 0.0 and out.max() <= 1.0
