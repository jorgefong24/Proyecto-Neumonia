#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pruebas unitarias para el módulo read_img.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.read_img import read_image, read_jpg_file


def test_read_image_nonexistent_path_raises():
    """
    Verifica que read_image lanza FileNotFoundError para ruta inexistente.
    """
    with pytest.raises(FileNotFoundError):
        read_image("/ruta/que/no/existe/archivo.dcm")


def test_read_jpg_file_nonexistent_path_raises():
    """
    Verifica que read_jpg_file lanza FileNotFoundError para ruta inexistente.
    """
    with pytest.raises(FileNotFoundError):
        read_jpg_file("/ruta/que/no/existe/imagen.jpg")
