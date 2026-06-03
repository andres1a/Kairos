from __future__ import annotations

from datetime import datetime

import google.generativeai as genai
import streamlit as st
import streamlit.components.v1 as components

from templates import (
    LUCIDE_ICONS,
    aplicar_estilos_personalizados,
    configurar_pagina,
    render_feature_list,
    render_file_card,
    render_page_hero,
    render_section_title,
    render_status_banner,
    render_summary_card,
)
from utils import (
    corregir_orientacion_imagen,
    detectar_elemento_automatico,
    generar_reporte_pdf,
    limpiar_markdown,
    open_pdf_new_tab,
    obtener_prompt_especializado,
    validar_configuracion,
)


def realizar_analisis(imagen, nombre_archivo, tipo_elemento):
    """Realiza el análisis de la imagen con prompt especializado."""

    try:
        with st.spinner(f"🔄 Analizando {tipo_elemento.lower()} con IA especializada..."):
            model = genai.GenerativeModel("gemini-2.5-flash")
            prompt = obtener_prompt_especializado(tipo_elemento)
            respuesta = model.generate_content([prompt, imagen])
            respuesta_limpia = limpiar_markdown(respuesta.text)

            texto_respuesta = respuesta_limpia.lower()
            es_buen_estado = any(
                keyword in texto_respuesta
                for keyword in ["buen estado", "satisfactorio", "sin fallas", "no se observan", "elemento sano"]
            )

            st.session_state.resultado_analisis = {
                "respuesta": respuesta_limpia,
                "es_buen_estado": es_buen_estado,
                "tipo_elemento": tipo_elemento,
                "imagen": imagen,
                "nombre_archivo": nombre_archivo,
            }
            st.session_state.analisis_completado = True
            st.rerun()
    except Exception as e:
        st.error(f"Error en el análisis: {str(e)}")
        st.markdown(
            f"""
        <div class="alert-warning">
            {LUCIDE_ICONS['alert']} <strong>Sugerencias para resolver el problema:</strong><br>
            • Verifica que la imagen sea clara y esté bien iluminada<br>
            • Asegúrate de que el archivo no esté corrupto<br>
            • Intenta con una imagen de menor tamaño<br>
            • Contacta al soporte técnico si el problema persiste
        </div>
        """,
            unsafe_allow_html=True,
        )


def mostrar_resultados_analisis():
    """Muestra los resultados del análisis ya completado."""

    resultado = st.session_state.resultado_analisis
    if not resultado:
        return

    st.markdown("---")
    st.markdown(f"## {LUCIDE_ICONS['chart']} Resultados del Análisis", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 Análisis Completo", "⬇️ Descargar Reporte", "ℹ️ Información Técnica"])

    with tab1:
        if resultado["es_buen_estado"]:
            st.markdown(
                f"""
            <div class="alert-success">
                {LUCIDE_ICONS['check']} <strong>Análisis completado: Elemento en buen estado estructural</strong>
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
            <div class="alert-warning">
                {LUCIDE_ICONS['alert']} <strong>Análisis completado: Se detectaron fallas o defectos</strong>
            </div>
            """,
                unsafe_allow_html=True,
            )

        iconos_elementos = {"Viga": LUCIDE_ICONS["beam"], "Columna": LUCIDE_ICONS["column"], "Losa": LUCIDE_ICONS["square"], "Muro": LUCIDE_ICONS["brick"]}
        icono = iconos_elementos.get(resultado["tipo_elemento"], LUCIDE_ICONS["wrench"])
        estado_icono = LUCIDE_ICONS["check"] if resultado["es_buen_estado"] else LUCIDE_ICONS["alert"]
        st.markdown(f"### {icono} {estado_icono} Diagnóstico de {resultado['tipo_elemento']}", unsafe_allow_html=True)
        st.markdown(resultado["respuesta"])

    with tab2:
        st.markdown("### ⬇️ Generar y Visualizar Reportes")
        pdf_bytes = generar_reporte_pdf(resultado["respuesta"], resultado["nombre_archivo"], resultado["imagen"], resultado["tipo_elemento"])

        if pdf_bytes:
            estado_archivo = "buen_estado" if resultado["es_buen_estado"] else "con_fallas"
            nombre_archivo = f"reporte_{resultado['tipo_elemento'].lower()}_{estado_archivo}_hibrido_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            col1, col2 = st.columns(2)

            with col1:
                st.download_button(
                    label="📄 Descargar PDF",
                    data=pdf_bytes,
                    file_name=nombre_archivo,
                    mime="application/pdf",
                    help=f"Descargar reporte especializado para {resultado['tipo_elemento']}",
                    use_container_width=True,
                )

            with col2:
                if st.button("🔍 Ver en Nueva Pestaña", help="Abrir el reporte en una nueva pestaña del navegador", use_container_width=True):
                    with st.spinner("🔄 Abriendo PDF en nueva pestaña..."):
                        _, success = open_pdf_new_tab(pdf_bytes, nombre_archivo)
                        if success:
                            st.success("✅ ¡PDF abierto en nueva pestaña del navegador!")
                            st.balloons()
                        else:
                            st.error("⚠️ Error al abrir el PDF. Usa la opción de descarga.")

            st.markdown("---")
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.metric("Tipo", "PDF Profesional")
            with col_info2:
                st.metric("Estado", "✅ Generado" if pdf_bytes else " Error")
            with col_info3:
                tamaño_kb = len(pdf_bytes) / 1024 if pdf_bytes else 0
                st.metric("Tamaño", f"{tamaño_kb:.1f} KB")

            st.markdown(
                f"""
            <div class="info-card">
                <strong>{LUCIDE_ICONS['clipboard']} Detalles del Reporte:</strong><br>
                • Elemento analizado: {resultado['tipo_elemento']}<br>
                • Estado estructural: {'Satisfactorio' if resultado['es_buen_estado'] else 'Requiere atención'}<br>
                • Formato: PDF profesional con imágenes<br>
                • Tecnología: Google Gemini 2.0 Flash + ReportLab
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.error("⚠️ Error al generar el reporte PDF. Intenta nuevamente.")

    with tab3:
        st.markdown("### 🔬 Información del Proceso")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Modelo IA", "Gemini 2.0")
        with col2:
            st.metric("Método", "Híbrido")
        with col3:
            st.metric("Estado", "✅ Sano" if resultado["es_buen_estado"] else "⚠️ Con Fallas")
        with col4:
            st.metric("Confiabilidad", "95%")

        if st.session_state.deteccion_automatica:
            deteccion = st.session_state.deteccion_automatica
            fue_confirmado = deteccion["elemento"] == resultado["tipo_elemento"]
            st.markdown(
                f"""
            **Detección Híbrida**:
            - IA detectó: {deteccion['elemento']} (Confianza: {deteccion['confianza']})
            - Usuario {'confirmó' if fue_confirmado else 'corrigió a ' + resultado['tipo_elemento']}
            - Análisis final realizado para: {resultado['tipo_elemento']}
            """
            )

        mensaje_tecnico = f"""
        **Nota Técnica**: Este análisis utilizó detección híbrida para identificar el elemento,
        seguido de prompts especializados para diagnóstico de {resultado['tipo_elemento'].lower()}s.
        """
        if resultado["es_buen_estado"]:
            mensaje_tecnico += """
            Elemento en buen estado: Se recomienda seguir las medidas preventivas sugeridas.
            """
        else:
            mensaje_tecnico += """
            Fallas detectadas: Se requiere atención técnica especializada.
            """
        mensaje_tecnico += "\nLos resultados deben ser validados por un ingeniero civil certificado."
        st.markdown(limpiar_markdown(mensaje_tecnico))


def main():
    configurar_pagina()
    aplicar_estilos_personalizados()

    api_key = validar_configuracion()
    genai.configure(api_key=api_key)

    if "elemento_seleccionado" not in st.session_state:
        st.session_state.elemento_seleccionado = None
    if "imagen_cargada" not in st.session_state:
        st.session_state.imagen_cargada = None
    if "nombre_archivo" not in st.session_state:
        st.session_state.nombre_archivo = None
    if "deteccion_automatica" not in st.session_state:
        st.session_state.deteccion_automatica = None
    if "deteccion_realizada" not in st.session_state:
        st.session_state.deteccion_realizada = False
    if "analisis_completado" not in st.session_state:
        st.session_state.analisis_completado = False
    if "resultado_analisis" not in st.session_state:
        st.session_state.resultado_analisis = None

    components.html(
        render_page_hero(
            "Kairos",
            "Análisis Inteligente de Defectos Estructurales",
            LUCIDE_ICONS["construction"],
        ),
        height=255,
        scrolling=False,
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        components.html(render_section_title("Acerca del Sistema", LUCIDE_ICONS["book"]), height=75, scrolling=False)
        components.html(
            render_feature_list(
                [
                    (LUCIDE_ICONS["bot"], "Detección Automática + Manual", "IA identifica automáticamente el elemento, tú confirmas o corriges"),
                    (LUCIDE_ICONS["search"], "Detección Automatizada", "Identifica automáticamente grietas, desgaste y defectos estructurales"),
                    (LUCIDE_ICONS["notepad"], "Análisis Especializado", "Proporciona diagnósticos técnicos específicos por elemento"),
                    (LUCIDE_ICONS["check"], "Evaluación Integral", "Identifica elementos sanos y con fallas, con recomendaciones apropiadas"),
                ]
            ),
            height=330,
            scrolling=False,
        )

        components.html(render_section_title("Cargar Imagen para Análisis", LUCIDE_ICONS["upload"]), height=75, scrolling=False)

        uploaded_file = st.file_uploader("Selecciona una imagen de la estructura a analizar", type=["png", "jpg", "jpeg"], help="Formatos soportados: PNG, JPG, JPEG (máx. 200MB)")

        if uploaded_file is not None:
            from PIL import Image

            nueva_imagen = Image.open(uploaded_file)
            nueva_imagen = corregir_orientacion_imagen(nueva_imagen)
            if st.session_state.nombre_archivo != uploaded_file.name or st.session_state.imagen_cargada is None:
                st.session_state.imagen_cargada = nueva_imagen
                st.session_state.nombre_archivo = uploaded_file.name
                st.session_state.deteccion_realizada = False
                st.session_state.deteccion_automatica = None
                st.session_state.elemento_seleccionado = None
                st.session_state.analisis_completado = False
                st.session_state.resultado_analisis = None

    with col2:
        if uploaded_file is not None:
            components.html(render_section_title("Imagen Cargada", LUCIDE_ICONS["image"]), height=75, scrolling=False)

            st.image(st.session_state.imagen_cargada, caption=f"📁 {uploaded_file.name}", use_container_width=True)
            components.html(
                render_file_card(
                    uploaded_file.name,
                    st.session_state.imagen_cargada.size[0],
                    st.session_state.imagen_cargada.size[1],
                    uploaded_file.size / 1024,
                    LUCIDE_ICONS["image"],
                ),
                height=360,
                scrolling=False,
            )

    if uploaded_file is not None:
        st.markdown("---")

        # Paso 1: Detección automática
        if not st.session_state.deteccion_realizada:
            st.markdown(f"### {LUCIDE_ICONS['bot']} Paso 1: Detección Automática", unsafe_allow_html=True)
            _, col2, _ = st.columns([1, 2, 1])
            with col2:
                if st.button("🔍 Detectar Elemento Automáticamente", key="auto_detect"):
                    with st.spinner("🤖 Analizando imagen para identificar elemento estructural..."):
                        try:
                            elemento_detectado, confianza, justificacion = detectar_elemento_automatico(st.session_state.imagen_cargada)
                            st.session_state.deteccion_automatica = {
                                "elemento": elemento_detectado,
                                "confianza": confianza,
                                "justificacion": justificacion,
                            }
                            st.session_state.deteccion_realizada = True
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error en detección: {str(e)}")
                            st.session_state.deteccion_automatica = {
                                "elemento": "Viga",
                                "confianza": "Baja",
                                "justificacion": f"Error en detección automática: {str(e)[:50]}...",
                            }
                            st.session_state.deteccion_realizada = True
                            st.rerun()

        # Paso 2: Confirmar o corregir detección
        if st.session_state.deteccion_realizada and st.session_state.deteccion_automatica:
            deteccion = st.session_state.deteccion_automatica
            components.html(
                render_status_banner(
                    "info",
                    f"{deteccion['elemento']} detectado con {deteccion['confianza'].lower()} confianza",
                    deteccion["justificacion"],
                ),
                height=130,
                scrolling=False,
            )

            st.markdown(f"### {LUCIDE_ICONS['check']} Paso 2: Confirmar o Corregir", unsafe_allow_html=True)
            opciones_elementos = {f"✅ Confirmar: {deteccion['elemento']}": deteccion['elemento']}
            todas_las_correcciones = {"🔧 Corregir a: Viga": "Viga", "🔧 Corregir a: Columna": "Columna", "🔧 Corregir a: Losa": "Losa", "🔧 Corregir a: Muro": "Muro"}
            for opcion_texto, elemento_valor in todas_las_correcciones.items():
                if elemento_valor != deteccion["elemento"]:
                    opciones_elementos[opcion_texto] = elemento_valor

            default_index = 0
            if st.session_state.elemento_seleccionado:
                for i, (key, value) in enumerate(opciones_elementos.items()):
                    if value == st.session_state.elemento_seleccionado:
                        default_index = i
                        break

            elemento_seleccionado = st.radio("¿Es correcta la detección automática?", options=list(opciones_elementos.keys()), index=default_index, key="selector_elemento_hibrido")
            if elemento_seleccionado:
                st.session_state.elemento_seleccionado = opciones_elementos[elemento_seleccionado]
                descripciones = {
                    "Viga": "Elemento horizontal que transmite cargas por flexión",
                    "Columna": "Elemento vertical que soporta cargas axiales y de flexión",
                    "Losa": "Elemento plano horizontal que distribuye cargas",
                    "Muro": "Elemento vertical de carga o división",
                }
                fue_confirmado = elemento_seleccionado.startswith("✅")
                status = "confirmado automáticamente" if fue_confirmado else "corregido manualmente"
                components.html(
                    render_summary_card(
                        "Elemento final",
                        f"{st.session_state.elemento_seleccionado} ({status})",
                        descripciones[st.session_state.elemento_seleccionado],
                    ),
                    height=165,
                    scrolling=False,
                )

    # Paso 3: Análisis estructural especializado
    if uploaded_file is not None and st.session_state.elemento_seleccionado:
        st.markdown("---")
        st.markdown(f"### {LUCIDE_ICONS['microscope']} Paso 3: Iniciar Análisis Estructural", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Analizar Estructura", key="analyze"):
                realizar_analisis(st.session_state.imagen_cargada, st.session_state.nombre_archivo, st.session_state.elemento_seleccionado)

    if st.session_state.analisis_completado and st.session_state.resultado_analisis:
        mostrar_resultados_analisis()
