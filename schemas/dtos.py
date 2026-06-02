from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from models import (
    ConfianzaEnum,
    EstadoCasoEnum,
    FormatoReporteEnum,
    OrigenDecisionEnum,
    PropositoModeloEnum,
    PropositoPlantillaEnum,
)


class SQLAlchemySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CatalogoElementoBase(SQLAlchemySchema):
    codigo: str = Field(..., max_length=20)
    nombre: str = Field(..., max_length=80)
    descripcion: str
    activo: bool = True


class CatalogoElementoCreate(CatalogoElementoBase):
    pass


class CatalogoElementoRead(CatalogoElementoBase):
    id_tipo_elemento: int


class ModeloIABase(SQLAlchemySchema):
    proveedor: str = Field(..., max_length=50)
    nombre_modelo: str = Field(..., max_length=100)
    version_modelo: str | None = Field(default=None, max_length=50)
    proposito: PropositoModeloEnum
    activo: bool = True


class ModeloIACreate(ModeloIABase):
    pass


class ModeloIARead(ModeloIABase):
    id_modelo_ia: int


class PlantillaPromptBase(SQLAlchemySchema):
    codigo: str = Field(..., max_length=80)
    proposito: PropositoPlantillaEnum
    id_tipo_elemento: int | None = None
    version: str = Field(default="1.0", max_length=20)
    texto_prompt: str
    activo: bool = True


class PlantillaPromptCreate(PlantillaPromptBase):
    pass


class PlantillaPromptRead(PlantillaPromptBase):
    id_plantilla_prompt: int


class CasoInspeccionBase(SQLAlchemySchema):
    estado: EstadoCasoEnum = EstadoCasoEnum.CARGADO
    nombre_archivo_origen: str
    tamano_archivo_bytes: int
    ancho_imagen: int
    alto_imagen: int
    uri_imagen_original: str
    hash_imagen_sha256: str | None = Field(default=None, max_length=64)


class CasoInspeccionCreate(CasoInspeccionBase):
    pass


class CasoInspeccionRead(CasoInspeccionBase):
    id_caso: int
    creado_en: datetime
    actualizado_en: datetime


class DeteccionAutomaticaBase(SQLAlchemySchema):
    id_caso: int
    numero_intento: int = 1
    id_modelo_ia: int
    id_plantilla_prompt: int
    id_tipo_elemento_detectado: int
    confianza: ConfianzaEnum
    justificacion: str
    respuesta_original: str


class DeteccionAutomaticaCreate(DeteccionAutomaticaBase):
    pass


class DeteccionAutomaticaRead(DeteccionAutomaticaBase):
    id_deteccion: int
    detectado_en: datetime


class SeleccionElementoBase(SQLAlchemySchema):
    id_caso: int
    id_deteccion_automatica: int
    id_tipo_elemento_seleccionado: int
    origen_decision: OrigenDecisionEnum


class SeleccionElementoCreate(SeleccionElementoBase):
    pass


class SeleccionElementoRead(SeleccionElementoBase):
    id_seleccion: int
    seleccionado_en: datetime


class AnalisisEstructuralBase(SQLAlchemySchema):
    id_caso: int
    numero_intento: int = 1
    id_modelo_ia: int
    id_plantilla_prompt: int
    id_tipo_elemento_analizado: int
    respuesta_original: str
    respuesta_limpia: str
    estado_bueno: bool
    puntaje_riesgo: int | None = None
    etiqueta_riesgo: str


class AnalisisEstructuralCreate(AnalisisEstructuralBase):
    pass


class AnalisisEstructuralRead(AnalisisEstructuralBase):
    id_analisis: int
    analizado_en: datetime


class ReporteAnalisisBase(SQLAlchemySchema):
    id_analisis: int
    formato_reporte: FormatoReporteEnum = FormatoReporteEnum.PDF
    nombre_archivo: str
    uri_archivo: str
    tamano_archivo_bytes: int
    tipo_mime: str = "application/pdf"


class ReporteAnalisisCreate(ReporteAnalisisBase):
    pass


class ReporteAnalisisRead(ReporteAnalisisBase):
    id_reporte: int
    generado_en: datetime
