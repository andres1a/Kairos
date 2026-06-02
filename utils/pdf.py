from __future__ import annotations

import tempfile
import webbrowser
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from utils.text import limpiar_markdown


def open_pdf_new_tab(pdf_bytes, filename: str = "reporte_kairos.pdf"):
    """Abre PDF en nueva pestaña del navegador."""

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", prefix="kairos_") as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_file_path = tmp_file.name

        webbrowser.open_new_tab(f"file://{tmp_file_path}")
        return tmp_file_path, True
    except Exception as e:
        import streamlit as st

        st.error(f"Error al abrir PDF: {str(e)}")
        return None, False


def generar_reporte_pdf(analisis, imagen_nombre, imagen_pil, tipo_elemento_seleccionado):
    """Genera un reporte profesional en PDF usando ReportLab."""

    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )

        styles = getSampleStyleSheet()
        titulo_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#2E5C3E"),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
        )
        subtitulo_style = ParagraphStyle(
            "CustomSubtitle",
            parent=styles["Heading2"],
            fontSize=16,
            textColor=colors.HexColor("#4A90A4"),
            spaceAfter=20,
            alignment=TA_CENTER,
        )
        texto_style = ParagraphStyle(
            "CustomNormal",
            parent=styles["Normal"],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            fontName="Helvetica",
        )

        story = []
        story.append(Paragraph("KAIROS", titulo_style))
        story.append(Paragraph("Reporte de Análisis Estructural", subtitulo_style))
        story.append(Spacer(1, 20))

        fecha_hora = datetime.now().strftime("%d/%m/%Y a las %H:%M")
        info_reporte = f"""
        <b>Fecha de Análisis:</b> {fecha_hora}<br/>
        <b>Imagen Analizada:</b> {imagen_nombre}<br/>
        <b>Elemento Estructural:</b> {tipo_elemento_seleccionado}<br/>
        <b>Método:</b> Detección Híbrida<br/>
        <b>Versión del Sistema:</b> Kairos 2.0<br/>
        <b>Tecnología:</b> Google Gemini 2.0 Flash
        """

        story.append(Paragraph("INFORMACIÓN DEL REPORTE", subtitulo_style))
        story.append(Paragraph(info_reporte, texto_style))
        story.append(Spacer(1, 20))

        if imagen_pil:
            story.append(Paragraph("IMAGEN ANALIZADA", subtitulo_style))
            img_width, img_height = imagen_pil.size
            max_width, max_height = 4 * inch, 3 * inch

            if img_width > max_width or img_height > max_height:
                ratio = min(max_width / img_width, max_height / img_height)
                new_width = img_width * ratio
                new_height = img_height * ratio
            else:
                new_width, new_height = img_width / 72 * inch, img_height / 72 * inch

            img_buffer = BytesIO()
            imagen_pil.save(img_buffer, format="PNG")
            img_buffer.seek(0)

            imagen_rl = RLImage(img_buffer, width=new_width, height=new_height)
            story.append(imagen_rl)
            story.append(Spacer(1, 20))

        story.append(Paragraph(f"ANÁLISIS DE {tipo_elemento_seleccionado.upper()}", subtitulo_style))
        analisis_limpio = limpiar_markdown(analisis)

        for paragrafo in analisis_limpio.split("\n\n"):
            if paragrafo.strip():
                paragrafo_limpio = paragrafo.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                story.append(Paragraph(paragrafo_limpio, texto_style))

        story.append(Spacer(1, 30))
        pie_pagina = f"""
        <i>Este reporte fue generado automáticamente por Kairos - Sistema de Análisis Estructural.<br/>
        Elemento analizado: {tipo_elemento_seleccionado} (Detección Híbrida)<br/>
        Los resultados deben ser validados por un ingeniero civil certificado.</i>
        """
        story.append(Paragraph(pie_pagina, texto_style))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        import streamlit as st

        st.error(f"Error generando PDF: {str(e)}")
        return None
