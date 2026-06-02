from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class PropositoModeloEnum(str, Enum):
    DETECCION = "DETECCION"
    ANALISIS = "ANALISIS"
    AMBOS = "AMBOS"


class PropositoPlantillaEnum(str, Enum):
    DETECCION = "DETECCION"
    ANALISIS = "ANALISIS"


class EstadoCasoEnum(str, Enum):
    CARGADO = "CARGADO"
    DETECTADO = "DETECTADO"
    SELECCIONADO = "SELECCIONADO"
    ANALIZADO = "ANALIZADO"
    REPORTE_GENERADO = "REPORTE_GENERADO"
    FALLIDO = "FALLIDO"


class ConfianzaEnum(str, Enum):
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAJA = "BAJA"


class OrigenDecisionEnum(str, Enum):
    CONFIRMACION = "CONFIRMACION"
    CORRECCION = "CORRECCION"


class FormatoReporteEnum(str, Enum):
    PDF = "PDF"


class CatalogoElemento(Base):
    __tablename__ = "catalogo_elementos"

    id_tipo_elemento: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    plantillas_prompt: Mapped[list[PlantillaPrompt]] = relationship(back_populates="elemento")
    detecciones_detectadas: Mapped[list[DeteccionAutomatica]] = relationship(
        back_populates="elemento_detectado",
        foreign_keys="DeteccionAutomatica.id_tipo_elemento_detectado",
    )
    selecciones: Mapped[list[SeleccionElemento]] = relationship(back_populates="elemento_seleccionado")
    analisis: Mapped[list[AnalisisEstructural]] = relationship(back_populates="elemento_analizado")


class ModeloIA(Base):
    __tablename__ = "modelo_ia"

    id_modelo_ia: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    proveedor: Mapped[str] = mapped_column(String(50), nullable=False)
    nombre_modelo: Mapped[str] = mapped_column(String(100), nullable=False)
    version_modelo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    proposito: Mapped[PropositoModeloEnum] = mapped_column(String(20), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint("proveedor", "nombre_modelo", "version_modelo", name="uq_modelo_ia"),
        CheckConstraint("proposito IN ('DETECCION', 'ANALISIS', 'AMBOS')", name="ck_modelo_ia_proposito"),
    )
    detecciones: Mapped[list[DeteccionAutomatica]] = relationship(back_populates="modelo_ia")
    analisis: Mapped[list[AnalisisEstructural]] = relationship(back_populates="modelo_ia")


class PlantillaPrompt(Base):
    __tablename__ = "plantilla_prompt"

    id_plantilla_prompt: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    proposito: Mapped[PropositoPlantillaEnum] = mapped_column(String(20), nullable=False)
    id_tipo_elemento: Mapped[int | None] = mapped_column(
        ForeignKey("catalogo_elementos.id_tipo_elemento", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=True,
    )
    version: Mapped[str] = mapped_column(String(20), nullable=False, default="1.0")
    texto_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        CheckConstraint("proposito IN ('DETECCION', 'ANALISIS')", name="ck_plantilla_prompt_proposito"),
        CheckConstraint(
            "(proposito = 'DETECCION' AND id_tipo_elemento IS NULL) OR (proposito = 'ANALISIS' AND id_tipo_elemento IS NOT NULL)",
            name="ck_plantilla_prompt_alcance",
        ),
    )

    elemento: Mapped[CatalogoElemento | None] = relationship(back_populates="plantillas_prompt")
    detecciones: Mapped[list[DeteccionAutomatica]] = relationship(back_populates="plantilla_prompt")
    analisis: Mapped[list[AnalisisEstructural]] = relationship(back_populates="plantilla_prompt")


class CasoInspeccion(Base):
    __tablename__ = "caso_inspeccion"

    id_caso: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    estado: Mapped[EstadoCasoEnum] = mapped_column(String(30), nullable=False, default=EstadoCasoEnum.CARGADO.value)
    nombre_archivo_origen: Mapped[str] = mapped_column(Text, nullable=False)
    tamano_archivo_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    ancho_imagen: Mapped[int] = mapped_column(Integer, nullable=False)
    alto_imagen: Mapped[int] = mapped_column(Integer, nullable=False)
    uri_imagen_original: Mapped[str] = mapped_column(Text, nullable=False)
    hash_imagen_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        CheckConstraint("estado IN ('CARGADO', 'DETECTADO', 'SELECCIONADO', 'ANALIZADO', 'REPORTE_GENERADO', 'FALLIDO')", name="ck_caso_inspeccion_estado"),
        CheckConstraint("tamano_archivo_bytes >= 0", name="ck_caso_inspeccion_tamano"),
        CheckConstraint("ancho_imagen > 0", name="ck_caso_inspeccion_ancho"),
        CheckConstraint("alto_imagen > 0", name="ck_caso_inspeccion_alto"),
    )

    detecciones: Mapped[list[DeteccionAutomatica]] = relationship(back_populates="caso", cascade="all, delete-orphan")
    seleccion: Mapped[SeleccionElemento | None] = relationship(back_populates="caso", uselist=False)
    analisis: Mapped[list[AnalisisEstructural]] = relationship(back_populates="caso", cascade="all, delete-orphan")


class DeteccionAutomatica(Base):
    __tablename__ = "deteccion_automatica"
    __table_args__ = (
        UniqueConstraint("id_caso", "numero_intento", name="uq_deteccion_caso_intento"),
        CheckConstraint("numero_intento > 0", name="ck_deteccion_automatica_intento"),
        CheckConstraint("confianza IN ('ALTA', 'MEDIA', 'BAJA')", name="ck_deteccion_automatica_confianza"),
    )

    id_deteccion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_caso: Mapped[int] = mapped_column(
        ForeignKey("caso_inspeccion.id_caso", onupdate="CASCADE", ondelete="CASCADE"), nullable=False
    )
    numero_intento: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    id_modelo_ia: Mapped[int] = mapped_column(
        ForeignKey("modelo_ia.id_modelo_ia", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False
    )
    id_plantilla_prompt: Mapped[int] = mapped_column(
        ForeignKey("plantilla_prompt.id_plantilla_prompt", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False
    )
    id_tipo_elemento_detectado: Mapped[int] = mapped_column(
        ForeignKey("catalogo_elementos.id_tipo_elemento", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False
    )
    confianza: Mapped[ConfianzaEnum] = mapped_column(String(10), nullable=False)
    justificacion: Mapped[str] = mapped_column(Text, nullable=False)
    respuesta_original: Mapped[str] = mapped_column(Text, nullable=False)
    detectado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    caso: Mapped[CasoInspeccion] = relationship(back_populates="detecciones")
    modelo_ia: Mapped[ModeloIA] = relationship(back_populates="detecciones")
    plantilla_prompt: Mapped[PlantillaPrompt] = relationship(back_populates="detecciones")
    elemento_detectado: Mapped[CatalogoElemento] = relationship(back_populates="detecciones_detectadas")
    seleccion: Mapped[SeleccionElemento | None] = relationship(back_populates="deteccion_automatica", uselist=False)


class SeleccionElemento(Base):
    __tablename__ = "seleccion_elemento"

    __table_args__ = (
        CheckConstraint("origen_decision IN ('CONFIRMACION', 'CORRECCION')", name="ck_seleccion_elemento_origen"),
    )

    id_seleccion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_caso: Mapped[int] = mapped_column(
        ForeignKey("caso_inspeccion.id_caso", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    id_deteccion_automatica: Mapped[int] = mapped_column(
        ForeignKey("deteccion_automatica.id_deteccion", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )
    id_tipo_elemento_seleccionado: Mapped[int] = mapped_column(
        ForeignKey("catalogo_elementos.id_tipo_elemento", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    origen_decision: Mapped[OrigenDecisionEnum] = mapped_column(String(20), nullable=False)
    seleccionado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    caso: Mapped[CasoInspeccion] = relationship(back_populates="seleccion")
    deteccion_automatica: Mapped[DeteccionAutomatica] = relationship(back_populates="seleccion")
    elemento_seleccionado: Mapped[CatalogoElemento] = relationship(back_populates="selecciones")


class AnalisisEstructural(Base):
    __tablename__ = "analisis_estructural"
    __table_args__ = (
        UniqueConstraint("id_caso", "numero_intento", name="uq_analisis_caso_intento"),
        CheckConstraint("numero_intento > 0", name="ck_analisis_estructural_intento"),
        CheckConstraint("puntaje_riesgo IS NULL OR (puntaje_riesgo BETWEEN 1 AND 10)", name="ck_analisis_estructural_riesgo"),
    )

    id_analisis: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_caso: Mapped[int] = mapped_column(
        ForeignKey("caso_inspeccion.id_caso", onupdate="CASCADE", ondelete="CASCADE"), nullable=False
    )
    numero_intento: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    id_modelo_ia: Mapped[int] = mapped_column(
        ForeignKey("modelo_ia.id_modelo_ia", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False
    )
    id_plantilla_prompt: Mapped[int] = mapped_column(
        ForeignKey("plantilla_prompt.id_plantilla_prompt", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False
    )
    id_tipo_elemento_analizado: Mapped[int] = mapped_column(
        ForeignKey("catalogo_elementos.id_tipo_elemento", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False
    )
    respuesta_original: Mapped[str] = mapped_column(Text, nullable=False)
    respuesta_limpia: Mapped[str] = mapped_column(Text, nullable=False)
    estado_bueno: Mapped[bool] = mapped_column(Boolean, nullable=False)
    puntaje_riesgo: Mapped[int | None] = mapped_column(Integer, nullable=True)
    etiqueta_riesgo: Mapped[str] = mapped_column(String(30), nullable=False)
    analizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    caso: Mapped[CasoInspeccion] = relationship(back_populates="analisis")
    modelo_ia: Mapped[ModeloIA] = relationship(back_populates="analisis")
    plantilla_prompt: Mapped[PlantillaPrompt] = relationship(back_populates="analisis")
    elemento_analizado: Mapped[CatalogoElemento] = relationship(back_populates="analisis")
    reporte: Mapped[ReporteAnalisis | None] = relationship(back_populates="analisis", uselist=False)


class ReporteAnalisis(Base):
    __tablename__ = "reporte_analisis"

    __table_args__ = (
        CheckConstraint("formato_reporte = 'PDF'", name="ck_reporte_analisis_formato"),
        CheckConstraint("tamano_archivo_bytes >= 0", name="ck_reporte_analisis_tamano"),
    )

    id_reporte: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_analisis: Mapped[int] = mapped_column(
        ForeignKey("analisis_estructural.id_analisis", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    formato_reporte: Mapped[FormatoReporteEnum] = mapped_column(String(10), nullable=False, default=FormatoReporteEnum.PDF.value)
    nombre_archivo: Mapped[str] = mapped_column(Text, nullable=False)
    uri_archivo: Mapped[str] = mapped_column(Text, nullable=False)
    tamano_archivo_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo_mime: Mapped[str] = mapped_column(String(50), nullable=False, default="application/pdf")
    generado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    analisis: Mapped[AnalisisEstructural] = relationship(back_populates="reporte")
