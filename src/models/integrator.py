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
    Ejecuta el pipeline completo de predicción y visualización.

    Args:
        array : Imagen en formato numpy (H, W) o (H, W, C).
        model_path : Ruta opcional al modelo .h5.

    Returns:
        tuple: (label, proba, heatmap) donde label es la clase predicha (str),
        proba es la probabilidad de neumonía (float) y heatmap 
        es un array RGB para visualización.
    """
    model = load_cnn_model(path=model_path)
    label, proba, heatmap = compute_grad_cam(model, array)
    return label, proba, heatmap
