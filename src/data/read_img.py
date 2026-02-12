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
    Lee un archivo DICOM y retorna el array y la imagen para mostrar.

    Args:
        path (str): Ruta al archivo DICOM 

    Raises:
        FileNotFoundError: Si el archivo no existe
        

    Returns:
        tuple: (img_rgb, img2show) donde img_rgb es un array RGB para el modelo
        y img2show es una imagen PIL para visualización.
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
    Lee un archivo de imagen JPG/PNG y retorna el array y la imagen.

    Args:
        path (str): Ruta al archivo de imagen JPG/PNG 

    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si el archivo no se pudo leer como imagen

    Returns:
        tuple: (img2, img2show) donde img2 es un numpy array
        e img2show es una imagen PIL para visualización.
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
    Lee una imagen desde archivo, detectando automáticamente el formato.
    
    Soporta archivos DICOM (.dcm) y formate raster (.jpg, .jpeg, .png).

    Args:
        path (str): Ruta al archivo de imagen (DICOM o JPG/PNG)

    Returns:
        tuple: (array, img2show) donde array es un numpy array
        e img2show es una imagen PIL para visualización.
    """
    path_lower = path.lower()
    if path_lower.endswith(".dcm"):
        return read_dicom_file(path)
    return read_jpg_file(path)
