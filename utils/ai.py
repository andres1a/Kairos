from __future__ import annotations

import streamlit as st
import google.generativeai as genai
from PIL import Image


def detectar_elemento_automatico(imagen: Image.Image):
    """Detecta automáticamente el tipo de elemento estructural en la imagen."""

    prompt_deteccion = """
    Eres un ingeniero estructural especializado. Analiza esta imagen y determina cuál es el ELEMENTO ESTRUCTURAL PRINCIPAL visible.

    ELEMENTOS POSIBLES:
    - Viga (elemento horizontal de concreto/acero)
    - Columna (elemento vertical de soporte)
    - Losa (superficie horizontal como piso/techo)
    - Muro (pared vertical de mampostería/concreto)

    RESPONDE EXACTAMENTE ASÍ:
    ELEMENTO: [Solo escribe: Viga, Columna, Losa o Muro]
    CONFIANZA: [Solo escribe: Alta, Media o Baja]
    JUSTIFICACIÓN: [Una línea explicando por qué]

    No agregues texto adicional. Sé preciso.
    """

    elemento_detectado = "Viga"
    confianza = "Media"
    justificacion = "Detección por defecto"

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        respuesta = model.generate_content([prompt_deteccion, imagen])

        if respuesta and respuesta.text:
            texto = respuesta.text.strip()
            for linea in texto.split("\n"):
                linea = linea.strip()
                if ":" not in linea:
                    continue
                clave, valor = linea.split(":", 1)
                clave = clave.strip().upper()
                valor = valor.strip()

                if "ELEMENTO" in clave:
                    for elem in ["Viga", "Columna", "Losa", "Muro"]:
                        if elem.lower() in valor.lower():
                            elemento_detectado = elem
                            break
                elif "CONFIANZA" in clave:
                    for conf in ["Alta", "Media", "Baja"]:
                        if conf.lower() in valor.lower():
                            confianza = conf
                            break
                elif "JUSTIFICACIÓN" in clave or "JUSTIFICACION" in clave:
                    justificacion = valor[:100]
        else:
            st.warning("⚠️ La IA no pudo procesar la imagen correctamente")
    except Exception as e:
        st.error(f"Error en detección automática: {str(e)}")
        elemento_detectado = "Viga"
        confianza = "Baja"
        justificacion = f"Error en detección: {str(e)[:50]}..."

    return elemento_detectado, confianza, justificacion


def obtener_prompt_especializado(tipo_elemento: str) -> str:
    """Obtiene el prompt especializado según el tipo de elemento estructural."""

    prompt_base = """
    Actúa como ingeniero civil especializado en patología de la construcción y análisis de fallas.

    Analiza la imagen proporcionada enfocándote específicamente en {elemento}.

    IMPORTANTE: Si NO observas fallas o defectos visibles en el elemento, indica claramente que el elemento se encuentra en BUEN ESTADO ESTRUCTURAL.
    """

    prompts_especificos = {
        "Viga": f"""{prompt_base.format(elemento="VIGAS")}
        FALLAS ESPECÍFICAS EN VIGAS A IDENTIFICAR:
        • Fallas por flexión: grietas verticales en la zona de momento máximo, deflexiones excesivas
        • Fallas por cortante: grietas diagonales a 45° cerca de los apoyos
        • Fallas por torsión: grietas helicoidales en vigas con cargas excéntricas
        • Fallas por fatiga: grietas progresivas por cargas repetitivas
        • Corrosión de armaduras longitudinales y estribos
        • Aplastamiento del concreto en zonas de compresión

        SI NO HAY FALLAS VISIBLES - REPORTAR COMO VIGA EN BUEN ESTADO:
        • Superficie del concreto uniforme y sin grietas significativas
        • Ausencia de deflexiones o deformaciones visibles
        • Recubrimiento de concreto íntegro
        • No hay signos de corrosión en armaduras expuestas
        • Conexiones con otros elementos en buenas condiciones

        RECOMENDACIONES ESPECÍFICAS:
        SI HAY FALLAS:
        • Reforzamiento con fibra de carbono o acero adicional
        • Inyección de grietas con resinas epóxicas
        • Instalación de apoyos temporales si es necesario

        SI NO HAY FALLAS (MANTENIMIENTO PREVENTIVO):
        • Inspección visual periódica cada 6 meses
        • Monitoreo de deflexiones bajo cargas de servicio
        • Protección anticorrosiva del recubrimiento
        """,
        "Columna": f"""{prompt_base.format(elemento="COLUMNAS")}
        FALLAS ESPECÍFICAS EN COLUMNAS A IDENTIFICAR:
        • Fallas por compresión: aplastamiento del concreto, pandeo
        • Fallas por flexocompresión: grietas en zonas de tracción
        • Corrosión de armaduras longitudinales y estribos
        • Fallas por cortante: grietas diagonales en la altura
        • Segregación del concreto por vibrado deficiente

        SI NO HAY FALLAS VISIBLES - REPORTAR COMO COLUMNA EN BUEN ESTADO:
        • Superficie del concreto sin grietas o fisuras
        • Ausencia de pandeo o desplome vertical
        • Recubrimiento uniforme y sin desprendimientos
        • No hay signos de corrosión en armaduras
        • Verticalidad adecuada del elemento

        RECOMENDACIONES ESPECÍFICAS:
        SI HAY FALLAS:
        • Encamisado con concreto reforzado o acero
        • Instalación de puntales o sistemas de apuntalamiento
        • Inyección de grietas y tratamiento de corrosión

        SI NO HAY FALLAS (MANTENIMIENTO PREVENTIVO):
        • Verificación de verticalidad anual con instrumentos
        • Inspección de juntas y conexiones semestralmente
        • Protección del concreto contra agentes agresivos
        """,
        "Losa": f"""{prompt_base.format(elemento="LOSAS")}
        FALLAS ESPECÍFICAS EN LOSAS A IDENTIFICAR:
        • Fallas por flexión: grietas en la cara inferior (zona de tracción)
        • Fallas por punzonamiento: grietas radiales alrededor de columnas
        • Deflexiones excesivas por sobrecarga o insuficiencia estructural
        • Corrosión de armaduras de refuerzo positivo y negativo
        • Desprendimiento del recubrimiento de concreto

        SI NO HAY FALLAS VISIBLES - REPORTAR COMO LOSA EN BUEN ESTADO:
        • Superficie uniforme sin grietas o fisuras
        • Ausencia de deflexiones o hundimientos visibles
        • No hay patrones de agrietamiento
        • Recubrimiento de concreto íntegro
        • Conexiones con columnas sin signos de punzonamiento

        RECOMENDACIONES ESPECÍFICAS:
        SI HAY FALLAS:
        • Reforzamiento con malla de acero adicional
        • Aplicación de sobrelosa de reforzamiento
        • Instalación de capiteles o ábacos en zonas críticas

        SI NO HAY FALLAS (MANTENIMIENTO PREVENTIVO):
        • Medición de deflexiones bajo cargas de servicio
        • Inspección de la cara inferior cada 6 meses
        • Control de sobrecargas y cambios de uso
        """,
        "Muro": f"""{prompt_base.format(elemento="MUROS DE CARGA Y MAMPOSTERÍA")}
        FALLAS ESPECÍFICAS EN MUROS A IDENTIFICAR:
        • Grietas verticales por asentamiento diferencial
        • Grietas horizontales por flexión fuera del plano
        • Grietas diagonales por esfuerzos cortantes (sismos)
        • Separación en juntas de construcción
        • Eflorescencias y deterioro de morteros

        SI NO HAY FALLAS VISIBLES - REPORTAR COMO MURO EN BUEN ESTADO:
        • Superficie sin grietas, fisuras o separaciones
        • Mortero de juntas en buenas condiciones
        • Ausencia de eflorescencias o manchas
        • Verticalidad y plomo adecuados
        • No hay pandeo lateral o abombamientos

        RECOMENDACIONES ESPECÍFICAS:
        SI HAY FALLAS:
        • Inyección de grietas con morteros especializados
        • Instalación de tensores o tirantes metálicos
        • Reforzamiento con geomallas o mallas de acero

        SI NO HAY FALLAS (MANTENIMIENTO PREVENTIVO):
        • Inspección visual trimestral de juntas y superficie
        • Control de humedad y ventilación adecuada
        • Verificación de verticalidad anual
        """,
    }

    prompt_final = prompts_especificos.get(tipo_elemento, prompts_especificos["Viga"])
    prompt_final += """

    FORMATO DE RESPUESTA ESTRICTO - SOLO TEXTO PLANO:
    1. ESTADO GENERAL: [Buen Estado / Con Fallas]
    2. DESCRIPCIÓN TÉCNICA: [Detalle del análisis]
    3. CALIFICACIÓN DE RIESGO: [1-10 o SATISFACTORIO]
    4. RECOMENDACIONES: [Preventivas o Correctivas]

    REGLAS DE FORMATO OBLIGATORIAS:
    - NO uses asteriscos (*) ni (**) para negrita
    - NO uses guiones (-) para listas
    - NO uses símbolos markdown
    - USA TEXTO PLANO únicamente
    - USA MAYÚSCULAS para títulos importantes
    - Separa secciones con líneas vacías
    - Usa viñetas con • si necesitas listas

    Responde únicamente en español con un análisis detallado y profesional.
    IMPORTANTE: Usa SOLO texto plano sin símbolos de formato.
    """
    return prompt_final
