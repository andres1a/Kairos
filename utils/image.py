from __future__ import annotations

import base64
from io import BytesIO

from PIL import Image


def corregir_orientacion_imagen(imagen: Image.Image) -> Image.Image:
    """Corrige la orientación de la imagen basándose en EXIF o proporciones."""

    try:
        return imagen.transpose(Image.Transpose.EXIF_TRANSPOSE)
    except Exception:
        try:
            width, height = imagen.size
            if width > height:
                imagen = imagen.rotate(90, expand=True)
            return imagen
        except Exception:
            return imagen


def imagen_a_base64(imagen: Image.Image) -> str:
    """Convierte imagen PIL a base64 para descargas o transporte."""

    buffer = BytesIO()
    imagen.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()
