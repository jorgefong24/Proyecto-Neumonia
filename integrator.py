#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Módulo integrador (Facade): coordina read_img, preprocess, load_model y
grad_cam para exponer una única salida hacia la interfaz gráfica.

Responsabilidad: unificar salidas y retornar solo clase, probabilidad
y heatmap para la UI.
"""

from load_model import load_model as load_cnn_model
from grad_cam import grad_cam as compute_grad_cam


def run_pipeline(array, model_path=None):
    """
    Ejecuta el flujo completo: modelo + predicción + Grad-CAM.

    Recibe el arreglo de imagen ya leído (por read_img), carga el modelo,
    obtiene predicción y mapa de calor y retorna lo necesario para la UI.

    Args:
        array: numpy array de la imagen (salida de read_img).
        model_path: Ruta opcional al archivo .h5 (None = conv_MLP_84.h5).

    Returns:
        tuple: (clase_str, probabilidad_0_a_1, heatmap_imagen_rgb).
        - clase_str: "bacteriana", "normal" o "viral".
        - probabilidad_0_a_1: float en [0, 1].
        - heatmap_imagen_rgb: numpy array (H, W, 3) uint8 para mostrar.
    """
    model = load_cnn_model(path=model_path)
    label, proba, heatmap = compute_grad_cam(model, array)
    return label, proba, heatmap
