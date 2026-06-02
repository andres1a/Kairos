# Kairos

Kairos es una aplicacion de analisis inteligente de defectos estructurales. La interfaz se ejecuta con Streamlit y la arquitectura actual ya esta dividida en capas: un punto de entrada ligero, un router de interfaz, plantillas HTML/Tailwind, utilidades reutilizables y una capa de persistencia con SQLAlchemy + SQLite.

## Arquitectura actual

El siguiente diagrama resume como se distribuyen los componentes en la aplicacion actual.

```mermaid
flowchart TD
    subgraph P[Presentacion]
        D[defect.py\nEntry point]
        R[apis/router.py\nRouter y orquestacion Streamlit]
        TUI[templates/ui.py\nEstilos, iconos y layout base]
        TH[templates/html.py\nPlantillas HTML y componentes Tailwind]
    end

    subgraph U[Utilidades]
        UT[utils/text.py\nLimpieza de markdown]
        UI[utils/image.py\nOrientacion y base64 de imagen]
        UC[utils/config.py\nCarga y validacion de API key]
        UP[utils/prompts.py\nPrompts IA y deteccion automatica]
        UPDF[utils/pdf.py\nGeneracion y apertura de PDF]
    end

    subgraph S[Persistencia]
        DB[database.py\nEngine, SessionLocal, init_db]
        M[models/entities.py\nEntidades ORM y relaciones]
        SCH[schemas/dtos.py\nDTOs Pydantic]
        SER[services/inspection.py\nServicios CRUD y flujo]
    end

    subgraph E[Dependencias externas]
        GAI[Google Generative AI\nGemini]
        STL[Streamlit]
        RL[ReportLab]
        PIL[Pillow]
        SQLITE[SQLite]
    end

    D --> R
    R --> TUI
    R --> TH
    R --> UC
    R --> UI
    R --> UP
    R --> UT
    R --> UPDF
    R --> GAI
    UP --> GAI
    UI --> PIL
    UPDF --> RL
    UPDF --> UT
    R --> STL
    TUI --> STL
    TH --> STL
    UC --> STL
    DB --> SQLITE
    DB --> M
    M --> SCH
    SER --> SCH
    SER --> M
    SER --> DB
    R -. flujo de negocio opcional .-> SER
```

## Diseno de base de datos

Este modelo captura el flujo real de trabajo: caso de inspeccion, deteccion automatica, seleccion final, analisis estructural y reporte.

```mermaid
erDiagram
    CATALOGO_ELEMENTOS ||--o{ PLANTILLA_PROMPT : define
    MODELO_IA ||--o{ DETECCION_AUTOMATICA : usa
    MODELO_IA ||--o{ ANALISIS_ESTRUCTURAL : usa
    PLANTILLA_PROMPT ||--o{ DETECCION_AUTOMATICA : guia
    PLANTILLA_PROMPT ||--o{ ANALISIS_ESTRUCTURAL : guia
    CASO_INSPECCION ||--o{ DETECCION_AUTOMATICA : contiene
    CASO_INSPECCION ||--|| SELECCION_ELEMENTO : termina_en
    CASO_INSPECCION ||--o{ ANALISIS_ESTRUCTURAL : produce
    ANALISIS_ESTRUCTURAL ||--|| REPORTE_ANALISIS : genera
    CATALOGO_ELEMENTOS ||--o{ DETECCION_AUTOMATICA : detecta_como
    CATALOGO_ELEMENTOS ||--o{ SELECCION_ELEMENTO : selecciona_como
    CATALOGO_ELEMENTOS ||--o{ ANALISIS_ESTRUCTURAL : analiza_como
```

```mermaid
flowchart TD
    CE[CATALOGO_ELEMENTOS\nTipos de elementos estructurales]
    MI[MODELO_IA\nModelos disponibles]
    PP[PLANTILLA_PROMPT\nPrompts reutilizables]
    CI[CASO_INSPECCION\nImagen e inspeccion del usuario]
    DA[DETECCION_AUTOMATICA\nResultado inicial de IA]
    SE[SELECCION_ELEMENTO\nConfirmacion o correccion del usuario]
    AE[ANALISIS_ESTRUCTURAL\nDiagnostico tecnico final]
    RA[REPORTE_ANALISIS\nPDF generado]

    CE --> PP
    CE --> DA
    CE --> SE
    CE --> AE
    MI --> DA
    MI --> AE
    PP --> DA
    PP --> AE
    CI --> DA
    CI --> SE
    CI --> AE
    AE --> RA
```

## Despliegue

El despliegue representa la ejecucion local o administrada de Streamlit, con Gemini como servicio externo y SQLite como almacenamiento local de metadatos.

```mermaid
flowchart LR
    subgraph C[Cliente]
        B[Browser web\nUsuario final]
    end

    subgraph A[Servidor de aplicacion]
        S[Streamlit runtime\ndefect.py -> apis/router.py]
        H[Templates HTML + Tailwind\ntemplates/]
        U[Utilidades de dominio\nutils/]
        P[Persistencia ORM\nmodels/ + schemas/ + services/]
    end

    subgraph D[Datos locales]
        F[Sistema de archivos\nImagenes originales\nPDF generados]
        DB[(SQLite\nKairos.db)]
    end

    subgraph X[Servicios externos]
        G[Google Generative AI\nGemini 2.5 Flash]
    end

    B -->|HTTP / WebSocket| S
    S --> H
    S --> U
    S --> P
    U --> G
    P --> DB
    U --> F
    S --> F
    S -->|respuesta renderizada| B
    P -. init_db / session_scope .-> DB
```

## Modulos principales

- [defect.py](defect.py) funciona como punto de entrada.
- [apis/router.py](apis/router.py) concentra el flujo de la interfaz y la orquestacion de la app.
- [templates/ui.py](templates/ui.py) define estilos, iconos y layout base.
- [templates/html.py](templates/html.py) contiene componentes HTML con Tailwind para la capa visual.
- [utils/](utils) agrupa configuracion, imagen, texto, prompts y PDF.
- [database.py](database.py), [models/entities.py](models/entities.py), [schemas/dtos.py](schemas/dtos.py) y [services/inspection.py](services/inspection.py) forman la capa de persistencia.

## Dependencias

Las dependencias principales del proyecto viven en [requirements.txt](requirements.txt): Streamlit, Google Generative AI, Pillow, ReportLab y SQLAlchemy, entre otras.

## Documentacion relacionada

- [diagrama de componentes](diagrama_componentes_kairos.md)
- [diseno de base de datos](diseno_bd_sqlite_kairos.md)
- [diagrama de despliegue](diagrama_despliegue_kairos.md)

## Funcion general

La aplicacion permite cargar una imagen, detectar automaticamente el elemento estructural, confirmar o corregir esa deteccion, ejecutar un analisis especializado y generar un reporte PDF con los resultados.
