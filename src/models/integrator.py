#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Módulo integrador (Facade): coordina read_img, preprocess, load_model y
grad_cam para exponer una única salida hacia la interfaz gráfica.

Responsabilidad: unificar salidas y retornar solo clase, probabilidad
y heatmap para la UI.
"""

from src.models.load_model import load_model as load_cnn_model
from src.visualizations.grad_cam import grad_cam as compute_grad_cam

def run_pipeline(array, model_path=None):
    """
    Ejecuta el pipeline: carga el modelo, predice y genera heatmap Grad-CAM.

    Args:
        array: Array numpy de la imagen (salida de read_image).
        model_path: Ruta opcional al archivo .h5. Si es None, se busca el
            modelo por defecto.

    Returns:
        Tupla (label, proba, heatmap_rgb) para la interfaz.
    """
    model = load_cnn_model(path=model_path)
    label, proba, heatmap = compute_grad_cam(model, array)
    return label, proba, heatmap
