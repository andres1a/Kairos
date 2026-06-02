from __future__ import annotations

import os

import streamlit as st


def validar_configuracion() -> str:
    """Obtiene la API key de Gemini desde secrets o variables de entorno."""

    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            if api_key and api_key.strip():
                return api_key

        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and api_key.strip():
            return api_key

        st.error("🔑 Error de Configuración: API key no encontrada")

        is_cloud = os.path.exists("/mount/src")

        if is_cloud:
            st.info(
                """
            📌 **Configuración en Streamlit Cloud:**

            1. Ve a tu app en https://share.streamlit.io/
            2. Haz clic en **Settings** (⚙️)
            3. Ve a **Secrets**
            4. Agrega esto:
            ```
            GEMINI_API_KEY = "tu_clave_api_aqui"
            ```
            5. Guarda y reinicia la app
            """
            )
        else:
            st.info(
                """
            📌 **Configuración Local:**

            Crea un archivo `.streamlit/secrets.toml` en tu proyecto con:
            ```
            GEMINI_API_KEY = "tu_clave_api_aqui"
            ```

            O crea un archivo `.env` con:
            ```
            GEMINI_API_KEY=tu_clave_api_aqui
            ```
            """
            )

        st.stop()
    except Exception as e:
        st.error(f"❌ Error de Configuración: {str(e)}")
        st.stop()
