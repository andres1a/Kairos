from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import (
    AnalisisEstructural,
    CasoInspeccion,
    CatalogoElemento,
    DeteccionAutomatica,
    ModeloIA,
    PlantillaPrompt,
    ReporteAnalisis,
    SeleccionElemento,
)
from schemas import (
    AnalisisEstructuralCreate,
    CasoInspeccionCreate,
    CatalogoElementoCreate,
    DeteccionAutomaticaCreate,
    ModeloIACreate,
    PlantillaPromptCreate,
    ReporteAnalisisCreate,
    SeleccionElementoCreate,
)


ModelT = TypeVar("ModelT")
CreateSchemaT = TypeVar("CreateSchemaT", bound=BaseModel)


class ServicioBase(Generic[ModelT, CreateSchemaT]):
    def __init__(self, session: Session):
        self.session = session

    def obtener_por_id(self, modelo: type[ModelT], identificador: int) -> ModelT | None:
        return self.session.get(modelo, identificador)

    def listar(self, modelo: type[ModelT], limite: int = 100, desplazamiento: int = 0) -> list[ModelT]:
        consulta = select(modelo).limit(limite).offset(desplazamiento)
        return list(self.session.scalars(consulta).all())

    def crear(self, objeto: ModelT) -> ModelT:
        self.session.add(objeto)
        self.session.commit()
        self.session.refresh(objeto)
        return objeto

    def eliminar(self, objeto: ModelT) -> None:
        self.session.delete(objeto)
        self.session.commit()


class CatalogoElementoService(ServicioBase[CatalogoElemento, CatalogoElementoCreate]):
    def crear_elemento(self, datos: CatalogoElementoCreate) -> CatalogoElemento:
        return self.crear(CatalogoElemento(**datos.model_dump()))


class ModeloIAService(ServicioBase[ModeloIA, ModeloIACreate]):
    def crear_modelo(self, datos: ModeloIACreate) -> ModeloIA:
        return self.crear(ModeloIA(**datos.model_dump()))


class PlantillaPromptService(ServicioBase[PlantillaPrompt, PlantillaPromptCreate]):
    def crear_plantilla(self, datos: PlantillaPromptCreate) -> PlantillaPrompt:
        return self.crear(PlantillaPrompt(**datos.model_dump()))


class CasoInspeccionService(ServicioBase[CasoInspeccion, CasoInspeccionCreate]):
    def crear_caso(self, datos: CasoInspeccionCreate) -> CasoInspeccion:
        return self.crear(CasoInspeccion(**datos.model_dump()))

    def actualizar_estado(self, id_caso: int, estado: str) -> CasoInspeccion:
        caso = self.session.get(CasoInspeccion, id_caso)
        if caso is None:
            raise LookupError(f"No existe el caso {id_caso}")
        caso.estado = estado
        self.session.commit()
        self.session.refresh(caso)
        return caso

    def obtener_caso_completo(self, id_caso: int) -> CasoInspeccion | None:
        return self.session.get(CasoInspeccion, id_caso)


class DeteccionAutomaticaService(ServicioBase[DeteccionAutomatica, DeteccionAutomaticaCreate]):
    def registrar_deteccion(self, datos: DeteccionAutomaticaCreate) -> DeteccionAutomatica:
        return self.crear(DeteccionAutomatica(**datos.model_dump()))


class SeleccionElementoService(ServicioBase[SeleccionElemento, SeleccionElementoCreate]):
    def registrar_seleccion(self, datos: SeleccionElementoCreate) -> SeleccionElemento:
        return self.crear(SeleccionElemento(**datos.model_dump()))


class AnalisisEstructuralService(ServicioBase[AnalisisEstructural, AnalisisEstructuralCreate]):
    def registrar_analisis(self, datos: AnalisisEstructuralCreate) -> AnalisisEstructural:
        return self.crear(AnalisisEstructural(**datos.model_dump()))


class ReporteAnalisisService(ServicioBase[ReporteAnalisis, ReporteAnalisisCreate]):
    def registrar_reporte(self, datos: ReporteAnalisisCreate) -> ReporteAnalisis:
        return self.crear(ReporteAnalisis(**datos.model_dump()))


class FlujoInspeccionService:
    def __init__(self, session: Session):
        self.session = session
        self.catalogos = CatalogoElementoService(session)
        self.modelos = ModeloIAService(session)
        self.plantillas = PlantillaPromptService(session)
        self.casos = CasoInspeccionService(session)
        self.detecciones = DeteccionAutomaticaService(session)
        self.selecciones = SeleccionElementoService(session)
        self.analisis = AnalisisEstructuralService(session)
        self.reportes = ReporteAnalisisService(session)

    def crear_caso_inspeccion(self, datos: CasoInspeccionCreate) -> CasoInspeccion:
        return self.casos.crear_caso(datos)

    def registrar_deteccion_automatica(self, datos: DeteccionAutomaticaCreate) -> DeteccionAutomatica:
        caso = self.session.get(CasoInspeccion, datos.id_caso)
        if caso is None:
            raise LookupError(f"No existe el caso {datos.id_caso}")
        return self.detecciones.registrar_deteccion(datos)

    def registrar_seleccion_elemento(self, datos: SeleccionElementoCreate) -> SeleccionElemento:
        caso = self.session.get(CasoInspeccion, datos.id_caso)
        if caso is None:
            raise LookupError(f"No existe el caso {datos.id_caso}")
        return self.selecciones.registrar_seleccion(datos)

    def registrar_analisis_estructural(self, datos: AnalisisEstructuralCreate) -> AnalisisEstructural:
        caso = self.session.get(CasoInspeccion, datos.id_caso)
        if caso is None:
            raise LookupError(f"No existe el caso {datos.id_caso}")
        return self.analisis.registrar_analisis(datos)

    def registrar_reporte_analisis(self, datos: ReporteAnalisisCreate) -> ReporteAnalisis:
        analisis = self.session.get(AnalisisEstructural, datos.id_analisis)
        if analisis is None:
            raise LookupError(f"No existe el analisis {datos.id_analisis}")
        return self.reportes.registrar_reporte(datos)
