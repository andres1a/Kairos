# ============================================================================
# BIBLIOTECAS Y CONFIGURACIÓN INICIAL
# ============================================================================

import os
import streamlit as st 
import google.generativeai as genai
from PIL import Image, ExifTags
import PIL.ExifTags
#from dotenv import load_dotenv
import json
from datetime import datetime
import base64
from io import BytesIO
import re
import webbrowser
import tempfile

# Librerías para PDF
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

# Cargar variables de entorno


# ============================================================================
# SVG ICONS DE LUCIDE
# ============================================================================

LUCIDE_ICONS = {
    "construction": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="8" rx="1"/><path d="M17 14v7"/><path d="M7 14v7"/><path d="M17 3v3"/><path d="M7 3v3"/><path d="M10 14 2.3 6.3"/><path d="m14 6 7.7 7.7"/><path d="m8 6 8 8"/></svg>''',
    "book": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 7v14"/><path d="M16 12h2"/><path d="M16 8h2"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/><path d="M6 12h2"/><path d="M6 8h2"/></svg>''',
    "bot": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>''',
    "search": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21 21-4.34-4.34"/><circle cx="11" cy="11" r="8"/></svg>''',
    "notepad": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2v4"/><path d="M12 2v4"/><path d="M16 2v4"/><rect width="16" height="18" x="4" y="4" rx="2"/><path d="M8 10h6"/><path d="M8 14h8"/><path d="M8 18h5"/></svg>''',
    "check": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>''',
    "upload": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17,8 12,3 7,8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>''',
    "image": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="m21 15-5-5L5 21"/></svg>''',
    "microscope": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 18h8"/><path d="M3 22h18"/><path d="M14 22a7 7 0 1 0 0-14h-1"/><path d="M9 14h2"/><path d="M9 12a2 2 0 0 1-2-2V6l6-4 6 4v4a2 2 0 0 1-2 2Z"/></svg>''',
    "rocket": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/></svg>''',
    "rotation": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2.5 2v6h6M2.66 15.57a10 10 0 1 0 .57-8.38"/></svg>''',
    "beam": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12h18"/><path d="M3 18h18"/><path d="M3 6h18"/></svg>''',
    "column": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v18"/><path d="M8 21h8"/><path d="M8 3h8"/></svg>''',
    "square": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/></svg>''',
    "brick": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="12" x="3" y="8" rx="1"/><path d="M10 8V5c0-.6-.4-1-1-1H6c-.6 0-1 .4-1 1v3"/><path d="M19 8V5c0-.6-.4-1-1-1h-3c-.6 0-1 .4-1 1v3"/></svg>''',
    "wrench": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>''',
    "info": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>''',
    "clipboard": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/></svg>''',
    "download": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-15"/><polyline points="7,10 12,15 17,10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>''',
    "chart": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>''',
    "alert": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="m12 17.02.01 0"/></svg>'''
}

# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================

st.set_page_config(
    page_title='Kairos - Análisis de Defectos Estructurales',
    page_icon='img\logok.jpeg',
    layout='wide',
    initial_sidebar_state='expanded'
)

# ============================================================================
# CSS PERSONALIZADO PARA DISEÑO PROFESIONAL
# ============================================================================

def aplicar_estilos_personalizados():
    st.markdown("""
    <style>
    /* Importar fuente profesional */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Variables CSS para consistencia */
    :root {
        --primary-color: #2E5C3E;
        --secondary-color: #4A90A4;
        --accent-color: #FFB703;
        --success-color: #06D6A0;
        --warning-color: #FB8500;
        --error-color: #E63946;
        --text-primary: #2D3748;
        --text-secondary: #718096;
        --background-light: #F7FAFC;
        --border-light: #E2E8F0;
    }
    
    /* Fuente global */
    .main, .sidebar .sidebar-content {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header principal */
    .main-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        color: white !important;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        margin: 0 !important;
        text-align: center;
    }
    
    .main-header .subtitle {
        color: rgba(255,255,255,0.9) !important;
        font-size: 1.2rem !important;
        text-align: center;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* Cards profesionales */
    .info-card {
        background: #0e1117;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid var(--border-light);
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin: 1rem 0;
    }
    
    .feature-card {
        background: var(--background-light);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid var(--primary-color);
        margin: 0.5rem 0;
    }
    
    /* Botones personalizados */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    }
    
    /* Alertas personalizadas */
    .alert-success {
        background: rgba(6, 214, 160, 0.1);
        border: 1px solid var(--success-color);
        border-radius: 8px;
        padding: 1rem;
        color: var(--success-color);
        font-weight: 500;
    }
    
    .alert-warning {
        background: rgba(251, 133, 0, 0.1);
        border: 1px solid var(--warning-color);
        border-radius: 8px;
        padding: 1rem;
        color: var(--warning-color);
        font-weight: 500;
    }
    
    /* Métricas mejoradas */
    .metric-card {
        background: #0e1117;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid var(--border-light);
    }
    
    /* Selector de elemento estructural */
    .element-selector {
        background: #0e1117;
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid white;
        margin: 2rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .element-selector h3 {
        color: #e2e9e5;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    /* Detección automática */
    .auto-detection {
        background: linear-gradient(135deg, #4A90A4 0%, #2E5C3E 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: white;
        text-align: center;
    }
    
    .confidence-alta { color: #06D6A0; font-weight: bold; }
    .confidence-media { color: #FFB703; font-weight: bold; }
    .confidence-baja { color: #FB8500; font-weight: bold; }
    
    /* SVG styling */
    .lucide-icon {
        display: inline-block;
        vertical-align: middle;
        margin-right: 8px;
    }
    
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def limpiar_markdown(texto):
    """Limpia asteriscos y otros símbolos markdown del texto"""
    
    # Eliminar asteriscos de negrita (**texto**)
    texto = re.sub(r'\*\*(.*?)\*\*', r'\1', texto)
    
    # Eliminar asteriscos simples (*texto*)  
    texto = re.sub(r'\*(.*?)\*', r'\1', texto)
    
    # Limpiar asteriscos sueltos
    texto = texto.replace('**', '')
    texto = texto.replace('*', '')
    
    # Limpiar otros símbolos markdown comunes
    texto = re.sub(r'#{1,6}\s', '', texto)  # Headers ###
    texto = re.sub(r'`(.*?)`', r'\1', texto)  # Código `texto`
    texto = re.sub(r'_(.*?)_', r'\1', texto)  # Cursiva _texto_
    texto = re.sub(r'~~(.*?)~~', r'\1', texto)  # Tachado ~~texto~~
    
    return texto.strip()

def corregir_orientacion_imagen(imagen):
    """Corrige la orientación de la imagen basándose en datos EXIF o dimensiones"""
    try:
        # Método 1: Usar EXIF automático (más simple y efectivo)
        imagen_corregida = imagen.transpose(Image.Transpose.EXIF_TRANSPOSE)
        return imagen_corregida
    except Exception:
        try:
            # Método 2: Verificar manualmente si necesita rotación
            width, height = imagen.size
            
            # Si la imagen es más ancha que alta, probablemente esté rotada
            if width > height:
                # Rotar 90 grados en sentido horario para enderezarla
                imagen = imagen.rotate(90, expand=True)
            
            return imagen
        except Exception:
            # Si todo falla, devolver la imagen original
            return imagen

def open_pdf_new_tab(pdf_bytes, filename="reporte_kairos.pdf"):
    """Abre PDF en nueva pestaña del navegador"""
    try:
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", prefix="kairos_") as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_file_path = tmp_file.name
        
        # Abrir en nueva pestaña
        webbrowser.open_new_tab(f'file://{tmp_file_path}')
        
        return tmp_file_path, True
        
    except Exception as e:
        st.error(f"Error al abrir PDF: {str(e)}")
        return None, False

def validar_configuracion():
    """Valida que la configuración esté correcta y obtiene la API key de forma segura"""
    try:
        # MÉTODO 1: Intentar obtener desde Streamlit Secrets (PRODUCCIÓN)
        if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
            api_key = st.secrets['GEMINI_API_KEY']
            if api_key and api_key.strip() != '':
                return api_key
        
        # MÉTODO 2: Intentar obtener desde variables de entorno (LOCAL)
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key and api_key.strip() != '':
            return api_key
        
        # Si no se encuentra en ningún lugar, mostrar error detallado
        st.error("🔑 Error de Configuración: API key no encontrada")
        
        # Detectar si estamos en Streamlit Cloud o local
        is_cloud = os.path.exists('/mount/src')  # Streamlit Cloud usa /mount/src
        
        if is_cloud:
            st.info("""
            📌 **Configuración en Streamlit Cloud:**
            
            1. Ve a tu app en https://share.streamlit.io/
            2. Haz clic en **Settings** (⚙️)
            3. Ve a **Secrets**
            4. Agrega esto:
            ```
            GEMINI_API_KEY = "tu_clave_api_aqui"
            ```
            5. Guarda y reinicia la app
            """)
        else:
            st.info("""
            📌 **Configuración Local:**
            
            Crea un archivo `.streamlit/secrets.toml` en tu proyecto con:
            ```
            GEMINI_API_KEY = "tu_clave_api_aqui"
            ```
            
            O crea un archivo `.env` con:
            ```
            GEMINI_API_KEY=tu_clave_api_aqui
            ```
            """)
        
        st.stop()
        
    except Exception as e:
        st.error(f"❌ Error de Configuración: {str(e)}")
        st.stop()


def detectar_elemento_automatico(imagen):
    """Detecta automáticamente el tipo de elemento estructural en la imagen"""
    
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
    
    elemento_detectado = "Viga"  # Default seguro
    confianza = "Media"
    justificacion = "Detección por defecto"
    
    try:
        # Crear modelo y generar contenido
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        respuesta = model.generate_content([prompt_deteccion, imagen])
        
        if respuesta and respuesta.text:
            texto = respuesta.text.strip()
            
            # Parsear línea por línea de manera más robusta
            lineas = texto.split('\n')
            
            for linea in lineas:
                linea = linea.strip()
                if ':' in linea:
                    clave, valor = linea.split(':', 1)
                    clave = clave.strip().upper()
                    valor = valor.strip()
                    
                    if 'ELEMENTO' in clave:
                        # Validar que sea uno de los elementos válidos
                        elementos_validos = ['Viga', 'Columna', 'Losa', 'Muro']
                        for elem in elementos_validos:
                            if elem.lower() in valor.lower():
                                elemento_detectado = elem
                                break
                    
                    elif 'CONFIANZA' in clave:
                        confianzas_validas = ['Alta', 'Media', 'Baja']
                        for conf in confianzas_validas:
                            if conf.lower() in valor.lower():
                                confianza = conf
                                break
                    
                    elif 'JUSTIFICACIÓN' in clave or 'JUSTIFICACION' in clave:
                        justificacion = valor[:100]  # Limitar longitud
            
        else:
            st.warning("⚠️ La IA no pudo procesar la imagen correctamente")
            
    except Exception as e:
        st.error(f" Error en detección automática: {str(e)}")
        elemento_detectado = "Viga"
        confianza = "Baja"
        justificacion = f"Error en detección: {str(e)[:50]}..."
    
    return elemento_detectado, confianza, justificacion

def obtener_prompt_especializado(tipo_elemento):
    """Obtiene el prompt especializado según el tipo de elemento estructural"""
    
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
        """
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
    
    EJEMPLO DEL FORMATO CORRECTO:
    ESTADO GENERAL: Buen Estado
    
    DESCRIPCIÓN TÉCNICA: El elemento presenta una superficie uniforme sin grietas visibles...
    
    CALIFICACIÓN DE RIESGO: SATISFACTORIO
    
    RECOMENDACIONES: Inspección visual periódica cada 6 meses...
    
    Responde únicamente en español con un análisis detallado y profesional.
    IMPORTANTE: Usa SOLO texto plano sin símbolos de formato.
    """
    
    return prompt_final

def imagen_a_base64(imagen):
    """Convierte imagen PIL a base64 para descargas"""
    buffer = BytesIO()
    imagen.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

def generar_reporte_pdf(analisis, imagen_nombre, imagen_pil, tipo_elemento_seleccionado):
    """Genera un reporte profesional en PDF usando ReportLab"""
    try:
        # Crear buffer para el PDF
        buffer = BytesIO()
        
        # Crear documento PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Obtener estilos
        styles = getSampleStyleSheet()
        
        # Crear estilos personalizados
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2E5C3E'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitulo_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#4A90A4'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        texto_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            fontName='Helvetica'
        )
        
        # Lista de elementos para el PDF
        story = []
        
        # Título principal
        story.append(Paragraph("KAIROS", titulo_style))
        story.append(Paragraph("Reporte de Análisis Estructural", subtitulo_style))
        story.append(Spacer(1, 20))
        
        # Información del reporte
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
        
        # Imagen analizada
        if imagen_pil:
            story.append(Paragraph("IMAGEN ANALIZADA", subtitulo_style))
            
            # Redimensionar imagen para PDF
            img_width, img_height = imagen_pil.size
            max_width, max_height = 4*inch, 3*inch
            
            if img_width > max_width or img_height > max_height:
                ratio = min(max_width/img_width, max_height/img_height)
                new_width = img_width * ratio
                new_height = img_height * ratio
            else:
                new_width, new_height = img_width/72*inch, img_height/72*inch
            
            img_buffer = BytesIO()
            imagen_pil.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            imagen_rl = RLImage(img_buffer, width=new_width, height=new_height)
            story.append(imagen_rl)
            story.append(Spacer(1, 20))
        
        # Análisis estructural específico
        story.append(Paragraph(f"ANÁLISIS DE {tipo_elemento_seleccionado.upper()}", subtitulo_style))
        
        # APLICAR LIMPIEZA DE MARKDOWN AQUÍ ⭐
        analisis_limpio = limpiar_markdown(analisis)
        
        # Dividir el análisis en párrafos para mejor formato
        paragrafos = analisis_limpio.split('\n\n')
        for paragrafo in paragrafos:
            if paragrafo.strip():
                # Escapar caracteres especiales para ReportLab
                paragrafo_limpio = paragrafo.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(paragrafo_limpio, texto_style))
        
        story.append(Spacer(1, 30))
        
        # Pie de página
        pie_pagina = f"""
        <i>Este reporte fue generado automáticamente por Kairos - Sistema de Análisis Estructural.<br/>
        Elemento analizado: {tipo_elemento_seleccionado} (Detección Híbrida)<br/>
        Los resultados deben ser validados por un ingeniero civil certificado.</i>
        """
        story.append(Paragraph(pie_pagina, texto_style))
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer.getvalue()
        
    except Exception as e:
        st.error(f"Error generando PDF: {str(e)}")
        return None

# ============================================================================
# INTERFAZ PRINCIPAL
# ============================================================================

def main():
    # Aplicar estilos
    aplicar_estilos_personalizados()
    
    # Validar configuración
    api_key = validar_configuracion()
    genai.configure(api_key=api_key)
    
    # Inicializar session state mejorado
    if 'elemento_seleccionado' not in st.session_state:
        st.session_state.elemento_seleccionado = None
    if 'imagen_cargada' not in st.session_state:
        st.session_state.imagen_cargada = None
    if 'nombre_archivo' not in st.session_state:
        st.session_state.nombre_archivo = None
    if 'deteccion_automatica' not in st.session_state:
        st.session_state.deteccion_automatica = None
    if 'deteccion_realizada' not in st.session_state:
        st.session_state.deteccion_realizada = False
    if 'analisis_completado' not in st.session_state:
        st.session_state.analisis_completado = False
    if 'resultado_analisis' not in st.session_state:
        st.session_state.resultado_analisis = None
 
    # Header principal
    st.markdown(f"""
    <div class="main-header">
        <h1><span class="lucide-icon">{LUCIDE_ICONS['construction']}</span>Kairos</h1>
        <div class="subtitle">Análisis Inteligente de Defectos Estructurales</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Contenido principal en columnas
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Información sobre la aplicación
        st.markdown(f"""
<span style="vertical-align:middle; margin-right:8px;">
{LUCIDE_ICONS['book']}
</span>
<span style="font-size:1.8em; font-weight:700;vertical-align:middle;">Acerca del Sistema</span>
""", unsafe_allow_html=True)
        
        st.markdown(f"""
<div style='margin-bottom:25px;'>
  <div style='margin-bottom:6px; display: flex; align-items: center;'>
    <span style="margin-right:8px; display:inline-block;">
      {LUCIDE_ICONS['bot']}
    </span>
    <b>Detección Automática + Manual</b>
    <span style="margin-left:8px; color:#bbb;">IA identifica automáticamente el elemento, tú confirmas o corriges</span>
  </div>
  <div style='margin-bottom:6px; display: flex; align-items: center;'>
    <span style="margin-right:8px; display:inline-block;">
      {LUCIDE_ICONS['search']}
    </span>
    <b>Detección Automatizada</b>
    <span style="margin-left:8px; color:#bbb;">Identifica automáticamente grietas, desgaste y defectos estructurales</span>
  </div>
  <div style='margin-bottom:6px; display: flex; align-items: center;'>
    <span style="margin-right:8px; display:inline-block;">
      {LUCIDE_ICONS['notepad']}
    </span>
    <b>Análisis Especializado</b>
    <span style="margin-left:8px; color:#bbb;">Proporciona diagnósticos técnicos específicos por elemento</span>
  </div>
  <div style='margin-bottom:6px; display: flex; align-items: center;'>
    <span style="margin-right:8px; display:inline-block;">
      {LUCIDE_ICONS['check']}
    </span>
    <b>Evaluación Integral</b>
    <span style="margin-left:8px; color:#bbb;">Identifica elementos sanos y con fallas, con recomendaciones apropiadas</span>
  </div>
</div>
""", unsafe_allow_html=True)
        
        # Carga de imagen
        st.markdown(f"""
<span style="vertical-align:middle; margin-right:8px;">
{LUCIDE_ICONS['upload']}
</span>
<span style="font-size:1.3em; font-weight:700;vertical-align:middle;">Cargar Imagen para Análisis</span>
""", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Selecciona una imagen de la estructura a analizar",
            type=['png', 'jpg', 'jpeg'],
            help="Formatos soportados: PNG, JPG, JPEG (máx. 200MB)"
        )
        
        # Manejar cambio de imagen
        if uploaded_file is not None:
            nueva_imagen = Image.open(uploaded_file)
            nueva_imagen = corregir_orientacion_imagen(nueva_imagen)
            # Si es una imagen diferente, resetear todo
            if (st.session_state.nombre_archivo != uploaded_file.name or 
                st.session_state.imagen_cargada is None):
                
                st.session_state.imagen_cargada = nueva_imagen
                st.session_state.nombre_archivo = uploaded_file.name
                # Reset completo del estado
                st.session_state.deteccion_realizada = False
                st.session_state.deteccion_automatica = None
                st.session_state.elemento_seleccionado = None
                st.session_state.analisis_completado = False
                st.session_state.resultado_analisis = None
    
    with col2:
        if uploaded_file is not None:
            # Mostrar imagen cargada
            st.markdown(f"""
<span style="vertical-align:middle; margin-right:8px;">
{LUCIDE_ICONS['image']}
</span>
<span style="font-size:1.2em; font-weight:700;vertical-align:middle;">Imagen Cargada</span>
""", unsafe_allow_html=True)
            
            st.image(st.session_state.imagen_cargada, caption=f"📁 {uploaded_file.name}", use_container_width=True)
            
            # Información de la imagen
            st.markdown(f"""
            <div class="metric-card">
                <strong>Detalles del Archivo</strong><br>
                📏 {st.session_state.imagen_cargada.size[0]} × {st.session_state.imagen_cargada.size[1]} px<br>
                📊 {uploaded_file.size / 1024:.1f} KB
            </div>
            """, unsafe_allow_html=True)
    
    # Detección automática y selector de elemento estructural
    if uploaded_file is not None:
        st.markdown("---")
        
        # Paso 1: Detección automática
        if not st.session_state.deteccion_realizada:
            st.markdown(f"### {LUCIDE_ICONS['bot']} Paso 1: Detección Automática", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔍 Detectar Elemento Automáticamente", key="auto_detect"):
                    with st.spinner('🤖 Analizando imagen para identificar elemento estructural...'):
                        try:
                            elemento_detectado, confianza, justificacion = detectar_elemento_automatico(st.session_state.imagen_cargada)
                            
                            # Guardar resultado
                            st.session_state.deteccion_automatica = {
                                'elemento': elemento_detectado,
                                'confianza': confianza,
                                'justificacion': justificacion
                            }
                            st.session_state.deteccion_realizada = True
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error en detección: {str(e)}")
                            # Usar detección por defecto en caso de error
                            st.session_state.deteccion_automatica = {
                                'elemento': 'Viga',
                                'confianza': 'Baja',
                                'justificacion': f'Error en detección automática: {str(e)[:50]}...'
                            }
                            st.session_state.deteccion_realizada = True
                            st.rerun()
        
        # Paso 2: Mostrar resultado y selector
        if st.session_state.deteccion_realizada and st.session_state.deteccion_automatica:
            deteccion = st.session_state.deteccion_automatica
            
            # Mostrar detección automática
            confianza_class = f"confidence-{deteccion['confianza'].lower()}"
            
            st.markdown(f"""
            <div class="auto-detection">
                <h3>{LUCIDE_ICONS['bot']} Detección Automática Completada</h3>
                <p><strong>Elemento Identificado:</strong> {deteccion['elemento']}</p>
                <p><strong>Confianza:</strong> <span class="{confianza_class}">{deteccion['confianza']}</span></p>
                <p><strong>Justificación:</strong> {deteccion['justificacion']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Selector con confirmación/corrección
            st.markdown(f"### {LUCIDE_ICONS['check']} Paso 2: Confirmar o Corregir", unsafe_allow_html=True)
            
            # Empezar solo con la opción de confirmar
            opciones_elementos = {
                f"✅ Confirmar: {deteccion['elemento']}": deteccion['elemento']
            }
            
            # Definir todas las opciones de corrección - SIN SVG EN RADIO BUTTONS
            todas_las_correcciones = {
                "🔧 Corregir a: Viga": "Viga",
                "🔧 Corregir a: Columna": "Columna", 
                "🔧 Corregir a: Losa": "Losa",
                "🔧 Corregir a: Muro": "Muro"
            }
            
            # Agregar solo las opciones que NO sean el elemento detectado
            for opcion_texto, elemento_valor in todas_las_correcciones.items():
                if elemento_valor != deteccion['elemento']:
                    opciones_elementos[opcion_texto] = elemento_valor
            
            # Obtener índice de selección por defecto
            default_index = 0
            if st.session_state.elemento_seleccionado:
                for i, (key, value) in enumerate(opciones_elementos.items()):
                    if value == st.session_state.elemento_seleccionado:
                        default_index = i
                        break
            
            elemento_seleccionado = st.radio(
                "¿Es correcta la detección automática?",
                options=list(opciones_elementos.keys()),
                index=default_index,
                key="selector_elemento_hibrido"
            )
            
            if elemento_seleccionado:
                st.session_state.elemento_seleccionado = opciones_elementos[elemento_seleccionado]
                
                # Mostrar información del elemento seleccionado
                descripciones = {
                    "Viga": "Elemento horizontal que transmite cargas por flexión",
                    "Columna": "Elemento vertical que soporta cargas axiales y de flexión", 
                    "Losa": "Elemento plano horizontal que distribuye cargas",
                    "Muro": "Elemento vertical de carga o división"
                }
                
                fue_confirmado = elemento_seleccionado.startswith("✅")
                status = "confirmado automáticamente" if fue_confirmado else "corregido manualmente"
                
                st.success(f"**Elemento final**: {st.session_state.elemento_seleccionado} ({status})")
                st.info(f"**Descripción**: {descripciones[st.session_state.elemento_seleccionado]}")
    
    # Paso 3: Sección de análisis
    if uploaded_file is not None and st.session_state.elemento_seleccionado:
        st.markdown("---")
        st.markdown(f"### {LUCIDE_ICONS['microscope']} Paso 3: Iniciar Análisis Estructural", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Analizar Estructura", key="analyze"):
                realizar_analisis(
                    st.session_state.imagen_cargada, 
                    st.session_state.nombre_archivo,
                    st.session_state.elemento_seleccionado
                )
    
    # Mostrar resultados si ya se completó el análisis
    if st.session_state.analisis_completado and st.session_state.resultado_analisis:
        mostrar_resultados_analisis()

def realizar_analisis(imagen, nombre_archivo, tipo_elemento):
    """Realiza el análisis de la imagen con prompt especializado"""
    
    try:
        with st.spinner(f'🔄 Analizando {tipo_elemento.lower()} con IA especializada...'):
            # Inicializar modelo
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            
            # Obtener prompt especializado
            prompt = obtener_prompt_especializado(tipo_elemento)
            
            # Realizar análisis
            respuesta = model.generate_content([prompt, imagen])
            
            # LIMPIAR LA RESPUESTA INMEDIATAMENTE ⭐
            respuesta_limpia = limpiar_markdown(respuesta.text)
            
            # Determinar si el elemento está en buen estado basado en la respuesta
            texto_respuesta = respuesta_limpia.lower()
            es_buen_estado = any(keyword in texto_respuesta for keyword in 
                               ['buen estado', 'satisfactorio', 'sin fallas', 'no se observan', 'elemento sano'])
            
            # Guardar resultado en session state CON TEXTO YA LIMPIO
            st.session_state.resultado_analisis = {
                'respuesta': respuesta_limpia,  # ⭐ Guardar ya limpio
                'es_buen_estado': es_buen_estado,
                'tipo_elemento': tipo_elemento,
                'imagen': imagen,
                'nombre_archivo': nombre_archivo
            }
            st.session_state.analisis_completado = True
            
            # Rerun para mostrar resultados
            st.rerun()
    
    except Exception as e:
        st.error(f" Error en el análisis: {str(e)}")
        st.markdown(f"""
        <div class="alert-warning">
            {LUCIDE_ICONS['alert']} <strong>Sugerencias para resolver el problema:</strong><br>
            • Verifica que la imagen sea clara y esté bien iluminada<br>
            • Asegúrate de que el archivo no esté corrupto<br>
            • Intenta con una imagen de menor tamaño<br>
            • Contacta al soporte técnico si el problema persiste
        </div>
        """, unsafe_allow_html=True)

def mostrar_resultados_analisis():
    """Muestra los resultados del análisis ya completado"""
    resultado = st.session_state.resultado_analisis
    
    if not resultado:
        return
    
    # Mostrar resultados
    st.markdown("---")
    st.markdown(f"## {LUCIDE_ICONS['chart']} Resultados del Análisis", unsafe_allow_html=True)
    
    # Crear tabs para organizar la información
    tab1, tab2, tab3 = st.tabs([
        "📋 Análisis Completo", 
        "⬇️ Descargar Reporte", 
        "ℹ️ Información Técnica"
    ])
    
    with tab1:
        # Alerta diferente según el estado
        if resultado['es_buen_estado']:
            st.markdown(f"""
            <div class="alert-success">
                {LUCIDE_ICONS['check']} <strong>Análisis completado: Elemento en buen estado estructural</strong>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="alert-warning">
                {LUCIDE_ICONS['alert']} <strong>Análisis completado: Se detectaron fallas o defectos</strong>
            </div>
            """, unsafe_allow_html=True)
        
        # Mostrar elemento analizado
        iconos_elementos = {
            "Viga": LUCIDE_ICONS['beam'],
            "Columna": LUCIDE_ICONS['column'], 
            "Losa": LUCIDE_ICONS['square'],
            "Muro": LUCIDE_ICONS['brick']
        }
        
        icono = iconos_elementos.get(resultado['tipo_elemento'], LUCIDE_ICONS['wrench'])
        estado_icono = LUCIDE_ICONS['check'] if resultado['es_buen_estado'] else LUCIDE_ICONS['alert']
        st.markdown(f"### {icono} {estado_icono} Diagnóstico de {resultado['tipo_elemento']}", unsafe_allow_html=True)
        
        # YA NO NECESITAS LIMPIAR AQUÍ PORQUE YA ESTÁ LIMPIO ⭐
        st.markdown(resultado['respuesta'])
    
    with tab2:
        st.markdown(f"### ⬇️ Generar y Visualizar Reportes")
        
        # Generar PDF una sola vez
        pdf_bytes = generar_reporte_pdf(
            resultado['respuesta'], 
            resultado['nombre_archivo'], 
            resultado['imagen'],
            resultado['tipo_elemento']
        )
        
        if pdf_bytes:
            estado_archivo = "buen_estado" if resultado['es_buen_estado'] else "con_fallas"
            nombre_archivo = f"reporte_{resultado['tipo_elemento'].lower()}_{estado_archivo}_hibrido_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Crear columnas para las opciones
            col1, col2 = st.columns(2)
            
            with col1:
                # Botón para descargar
                st.download_button(
                    label="📄 Descargar PDF",
                    data=pdf_bytes,
                    file_name=nombre_archivo,
                    mime="application/pdf",
                    help=f"Descargar reporte especializado para {resultado['tipo_elemento']}",
                    use_container_width=True
                )
            
            with col2:
                # Botón para abrir en nueva pestaña
                if st.button("🔍 Ver en Nueva Pestaña", 
                            help="Abrir el reporte en una nueva pestaña del navegador",
                            use_container_width=True):
                    
                    with st.spinner("🔄 Abriendo PDF en nueva pestaña..."):
                        temp_path, success = open_pdf_new_tab(pdf_bytes, nombre_archivo)
                        
                        if success:
                            st.success("✅ ¡PDF abierto en nueva pestaña del navegador!")
                            st.balloons()
                        else:
                            st.error("⚠️ Error al abrir el PDF. Usa la opción de descarga.")
            
            # Información del reporte generado
            st.markdown("---")
            col_info1, col_info2, col_info3 = st.columns(3)
            
            with col_info1:
                st.metric("Tipo", "PDF Profesional")
            
            with col_info2:
                st.metric("Estado", "✅ Generado" if pdf_bytes else " Error")
            
            with col_info3:
                tamaño_kb = len(pdf_bytes) / 1024 if pdf_bytes else 0
                st.metric("Tamaño", f"{tamaño_kb:.1f} KB")
            
            # Nota técnica
            st.markdown(f"""
            <div class="info-card">
                <strong>{LUCIDE_ICONS['clipboard']} Detalles del Reporte:</strong><br>
                • Elemento analizado: {resultado['tipo_elemento']}<br>
                • Estado estructural: {'Satisfactorio' if resultado['es_buen_estado'] else 'Requiere atención'}<br>
                • Formato: PDF profesional con imágenes<br>
                • Tecnología: Google Gemini 2.0 Flash + ReportLab
            </div>
            """, unsafe_allow_html=True)
        
        else:
            st.error("⚠️ Error al generar el reporte PDF. Intenta nuevamente.")
    
    with tab3:
        st.markdown(f"### 🔬 Información del Proceso")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Modelo IA", "Gemini 2.0")
        with col2:
            st.metric("Método", "Híbrido")
        with col3:
            st.metric("Estado", "✅ Sano" if resultado['es_buen_estado'] else "⚠️ Con Fallas")
        with col4:
            st.metric("Confiabilidad", "95%")
        
        #        # Información sobre la detección
        if st.session_state.deteccion_automatica:
            deteccion = st.session_state.deteccion_automatica
            fue_confirmado = deteccion['elemento'] == resultado['tipo_elemento']
            
            st.markdown(f"""
            **Detección Híbrida**: 
            - IA detectó: {deteccion['elemento']} (Confianza: {deteccion['confianza']})
            - Usuario {'confirmó' if fue_confirmado else 'corrigió a ' + resultado['tipo_elemento']}
            - Análisis final realizado para: {resultado['tipo_elemento']}
            """)
        
        mensaje_tecnico = f"""
        **Nota Técnica**: Este análisis utilizó detección híbrida para identificar el elemento, 
        seguido de prompts especializados para diagnóstico de {resultado['tipo_elemento'].lower()}s.
        """
        
        if resultado['es_buen_estado']:
            mensaje_tecnico += """
            Elemento en buen estado: Se recomienda seguir las medidas preventivas sugeridas.
            """
        else:
            mensaje_tecnico += """
            Fallas detectadas: Se requiere atención técnica especializada.
            """
        
        mensaje_tecnico += "\nLos resultados deben ser validados por un ingeniero civil certificado."
        
        # LIMPIAR EL MENSAJE TÉCNICO TAMBIÉN ⭐
        mensaje_tecnico_limpio = limpiar_markdown(mensaje_tecnico)
        st.markdown(mensaje_tecnico_limpio)

# ============================================================================
# EJECUTAR APLICACIÓN
# ============================================================================

if __name__ == "__main__":
    main()

