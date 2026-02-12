#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pruebas unitarias para el módulo detector_neumonia y display_labels.

Verifican el mapeo de etiquetas (sin Qt) y la conversión PIL -> QPixmap
(requiere PySide6).
"""

import os
import sys

import pytest
from PIL import Image

pytest.importorskip("PySide6")

# Asegurar que el paquete del proyecto sea importable.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.display_labels import get_display_label


def test_get_display_label_mapping():
    """
    Verifica que get_display_label devuelve el texto correcto para cada
    etiqueta del modelo (normal, viral, bacteriana).
    """
    assert get_display_label("normal") == "Sin neumonía"
    assert get_display_label("viral") == "Neumonía viral"
    assert get_display_label("bacteriana") == "Neumonía bacteriana"


def test_get_display_label_unknown_returns_str():
    """
    Verifica que para una etiqueta no definida en el mapeo se devuelve
    la representación en string de la etiqueta.
    """
    assert get_display_label("desconocida") == "desconocida"
    assert get_display_label("") == ""


def test_pil_to_qpixmap_returns_valid_pixmap():
    """
    Verifica que pil_to_qpixmap convierte una imagen PIL a QPixmap
    con las dimensiones esperadas (escalado al tamaño solicitado).
    """
    pytest.importorskip("PySide6")
    from PySide6.QtGui import QPixmap

    # Imagen pequeña 10x10 RGB.

    from src.models.detector_neumonia import pil_to_qpixmap
    pil_img = Image.new("RGB", (10, 10), color=(128, 128, 128))
    size = 40
    pix = pil_to_qpixmap(pil_img, size=size)

    assert isinstance(pix, QPixmap)
    assert not pix.isNull()
    # Escalado mantiene aspecto; para 10x10 queda size x size.
    assert pix.width() == size
    assert pix.height() == size
