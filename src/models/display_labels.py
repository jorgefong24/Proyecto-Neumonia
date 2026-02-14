#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mapeo de etiquetas del modelo de neumonía a texto para la interfaz.

Módulo sin dependencias de Qt para poder probarlo de forma aislada.
"""

# Etiquetas del modelo -> texto visible en la UI.
LABEL_DISPLAY_MAP = {
    "normal": "Sin neumonía",
    "viral": "Neumonía viral",
    "bacteriana": "Neumonía bacteriana",
}


def get_display_label(label: str) -> str:
    """
    Devuelve el texto a mostrar para la etiqueta predicha por el modelo.

    Args:
        label: Etiqueta cruda del modelo (ej. 'normal', 'viral', 'bacteriana').

    Returns:
        Texto legible para la interfaz (ej. 'Sin neumonía').
    """
    return LABEL_DISPLAY_MAP.get(label, str(label))
