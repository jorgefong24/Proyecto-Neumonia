#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CLI para ejecutar inferencia (sin GUI) en contenedor.

Ejemplos:
  python cli.py --image path\to\image.dcm
  python cli.py --image path\to\image.png --out out_dir
  python cli.py --image path\to\image.png --model conv_MLP_84.h5
"""

import argparse
import json
import os
from pathlib import Path

import numpy as np
from PIL import Image

from src.models.integrator import run_pipeline
from src.data.read_img import read_image


def _save_heatmap_rgb(out_path: Path, heatmap_rgb: np.ndarray) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.fromarray(heatmap_rgb.astype(np.uint8), mode="RGB")
    img.save(out_path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inferencia neumonía + Grad-CAM (modo CLI)."
    )
    parser.add_argument(
        "--image",
        required=True,
        help="Ruta de imagen (.dcm/.jpg/.jpeg/.png).",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Ruta al modelo .h5 (opcional). Por defecto busca conv_MLP_84.h5.",
    )
    parser.add_argument(
        "--out",
        default="out",
        help="Carpeta de salida para el heatmap (default: out).",
    )
    parser.add_argument(
        "--heatmap-name",
        default="heatmap.png",
        help="Nombre del archivo de heatmap dentro de --out (default: heatmap.png).",
    )
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.is_file():
        raise FileNotFoundError(f"No se encontró la imagen: {image_path}")

    array, _ = read_image(str(image_path))
    label, proba, heatmap_rgb = run_pipeline(array, model_path=args.model)

    out_dir = Path(args.out)
    heatmap_path = out_dir / args.heatmap_name
    _save_heatmap_rgb(heatmap_path, heatmap_rgb)

    payload = {
        "image": str(image_path),
        "label": label,
        "probability": proba,
        "probability_pct": round(float(proba) * 100.0, 2),
        "heatmap_path": str(heatmap_path),
        "model": args.model or "conv_MLP_84.h5",
    }
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
