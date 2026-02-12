#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Módulo de lectura de imágenes DICOM y raster (JPG/PNG).

Responsabilidad: leer imagen desde ruta, convertir a arreglo numpy
y proveer representación para visualización en interfaz.
"""

import os

import cv2
import numpy as np
import pydicom
from PIL import Image


def read_dicom_file(path):
    """
    Lee un archivo DICOM y devuelve array RGB y imagen PIL para visualización.

    Args:
        path: Ruta al archivo .dcm.

    Returns:
        Tupla (img_rgb, img2show) con array numpy RGB y PIL Image.

    Raises:
        FileNotFoundError: Si el archivo no existe.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"No se encontró el archivo: {path}")
    dcm = pydicom.dcmread(path)
    img_array = dcm.pixel_array
    img2show = Image.fromarray(img_array)
    img2 = img_array.astype(float)
    img2 = (np.maximum(img2, 0) / img2.max()) * 255.0
    img2 = np.uint8(img2)
    img_rgb = cv2.cvtColor(img2, cv2.COLOR_GRAY2RGB)
    return img_rgb, img2show


def read_jpg_file(path):
    """
    Lee una imagen JPEG/PNG y devuelve array y imagen PIL para visualización.

    Args:
        path: Ruta al archivo .jpg, .jpeg o .png.

    Returns:
        Tupla (img_array, img2show) con array numpy y PIL Image.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si la imagen no pudo leerse.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"No se encontró el archivo: {path}")
    img = cv2.imread(path)
    if img is None:
        raise ValueError(f"No se pudo leer la imagen: {path}")
    img_array = np.asarray(img)
    img2show = Image.fromarray(img_array)
    img2 = img_array.astype(float)
    img2 = (np.maximum(img2, 0) / img2.max()) * 255.0
    img2 = np.uint8(img2)
    return img2, img2show


def read_image(path):
    """
    Lee una imagen desde ruta; soporta DICOM (.dcm) y raster (.jpg, .png).

    Args:
        path: Ruta al archivo de imagen.

    Returns:
        Tupla (array, img2show): array para el pipeline, PIL Image para UI.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si la imagen no pudo leerse (solo raster).
    """
    path_lower = path.lower()
    if path_lower.endswith(".dcm"):
        return read_dicom_file(path)
    return read_jpg_file(path)
