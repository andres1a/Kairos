from __future__ import annotations

import re


def limpiar_markdown(texto: str) -> str:
    """Limpia asteriscos y otros símbolos markdown del texto."""

    texto = re.sub(r"\*\*(.*?)\*\*", r"\1", texto)
    texto = re.sub(r"\*(.*?)\*", r"\1", texto)
    texto = texto.replace("**", "")
    texto = texto.replace("*", "")
    texto = re.sub(r"#{1,6}\s", "", texto)
    texto = re.sub(r"`(.*?)`", r"\1", texto)
    texto = re.sub(r"_(.*?)_", r"\1", texto)
    texto = re.sub(r"~~(.*?)~~", r"\1", texto)
    return texto.strip()
