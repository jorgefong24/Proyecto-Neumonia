#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Módulo de generación de mapa de calor Grad-CAM para explicabilidad.

Responsabilidad: integrar con el modelo, obtener predicción y capa
convolucional de interés y generar heatmap superpuesto.
Implementado con tf.GradientTape (compatible con TF2 eager execution).
"""

import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers

from preprocess_img import preprocess

CONV_LAYER_NAME = "conv10_thisone"
LABELS = ("bacteriana", "normal", "viral")


def _find_last_conv_layer(model):
    """
    Obtiene la última capa convolucional del modelo si existe.

    Returns:
        Objeto Layer o None.
    """
    for layer in reversed(model.layers):
        if isinstance(layer, layers.Conv2D):
            return layer
    return None


def _get_conv_layer(model, layer_name=None):
    """
    Obtiene la capa convolucional por nombre o la última conv.

    Args:
        model: Modelo Keras.
        layer_name: Nombre de capa opcional.

    Returns:
        Capa convolucional.
    """
    if layer_name:
        try:
            return model.get_layer(layer_name)
        except ValueError:
            pass
    layer = _find_last_conv_layer(model)
    if layer is None:
        raise ValueError(
            "No se encontró capa convolucional para Grad-CAM."
        )
    return layer


def predict_class_and_probability(model, batch_array):
    """
    Predice la clase y la probabilidad para un batch de entrada.

    Args:
        model: Modelo Keras compilado.
        batch_array: Array (1, H, W, C) ya preprocesado.

    Returns:
        tuple: (índice_clase, probabilidad_en_0_a_1, etiqueta_str).
    """
    preds = model.predict(batch_array, verbose=0)
    argmax = int(np.argmax(preds[0]))
    proba = float(np.max(preds[0]))
    label = LABELS[argmax] if 0 <= argmax < len(LABELS) else f"clase_{argmax}"
    return argmax, proba, label


def grad_cam(model, array, conv_layer_name=None):
    """
    Genera el mapa de calor Grad-CAM y la imagen superpuesta.

    Usa GradientTape (TF2 eager) para los gradientes. Recibe la imagen
    en arreglo, la preprocesa, obtiene la predicción y la capa
    convolucional de interés para producir el heatmap.

    Args:
        model: Modelo Keras ya cargado.
        array: Imagen en formato numpy (H, W) o (H, W, C) para superponer.
        conv_layer_name: Nombre de capa conv opcional (default CONV_LAYER_NAME).

    Returns:
        tuple: (clase_str, probabilidad_0_1, heatmap_imagen_rgb).
        heatmap_imagen_rgb es numpy array (512, 512, 3) uint8.
    """
    batch_img = preprocess(array)
    batch_tensor = tf.convert_to_tensor(batch_img, dtype=tf.float32)
    argmax, proba, label = predict_class_and_probability(model, batch_img)

    last_conv = _get_conv_layer(
        model, layer_name=conv_layer_name or CONV_LAYER_NAME
    )
    conv_model = tf.keras.Model(model.input, last_conv.output)
    pred_model = tf.keras.Model(model.input, model.output)

    with tf.GradientTape() as tape:
        conv_output = conv_model(batch_tensor)
        tape.watch(conv_output)
        preds = pred_model(batch_tensor)
        class_channel = preds[:, argmax]

    grads = tape.gradient(class_channel, conv_output)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    conv_output_value = conv_output[0].numpy()
    pooled_grads_value = pooled_grads.numpy()

    for filters in range(conv_output_value.shape[-1]):
        conv_output_value[:, :, filters] *= pooled_grads_value[filters]

    heatmap = np.mean(conv_output_value, axis=-1)
    heatmap = np.maximum(heatmap, 0)
    heatmap /= (np.max(heatmap) + 1e-8)
    heatmap = cv2.resize(
        heatmap,
        (batch_img.shape[2], batch_img.shape[1])
    )
    heatmap = np.uint8(255 * heatmap)
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

    img2 = cv2.resize(array, (512, 512))
    if len(img2.shape) == 2:
        img2 = cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR)
    hif = 0.8
    transparency = (heatmap * hif).astype(np.uint8)
    superimposed_img = cv2.add(transparency, img2)
    superimposed_img = superimposed_img.astype(np.uint8)
    heatmap_rgb = cv2.cvtColor(superimposed_img, cv2.COLOR_BGR2RGB)

    return label, proba, heatmap_rgb
