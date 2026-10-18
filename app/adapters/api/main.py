"""Adaptador de entrada HTTP: FastAPI."""

import os
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status

from app.adapters.api.esquemas import SimulacionSalida, SolicitudEntrada
from app.adapters.persistencia.memoria import RepositorioEnMemoria
from app.application.simular_credito import SimularCredito
from app.ports.repositorio import RepositorioSimulaciones

app = FastAPI(
    title="Simulador de Crédito API",
    description="Simula créditos con el sistema de amortización francés y evalúa políticas de crédito.",
    version="1.0.0",
)


@lru_cache
def obtener_repositorio() -> RepositorioSimulaciones:
    """Elige el adaptador según el entorno: DynamoDB en AWS, memoria en local."""
    tabla = os.environ.get("TABLA_SIMULACIONES")
    if tabla:
        from app.adapters.persistencia.dynamodb import RepositorioDynamoDB

        return RepositorioDynamoDB(tabla)
    return RepositorioEnMemoria()


def obtener_caso_de_uso(
    repositorio: Annotated[RepositorioSimulaciones, Depends(obtener_repositorio)],
) -> SimularCredito:
    return SimularCredito(repositorio)


CasoDeUso = Annotated[SimularCredito, Depends(obtener_caso_de_uso)]


@app.get("/salud", tags=["Sistema"])
def salud() -> dict[str, str]:
    return {"estado": "ok"}


@app.post(
    "/simulaciones",
    response_model=SimulacionSalida,
    status_code=status.HTTP_201_CREATED,
    tags=["Simulaciones"],
    summary="Simular un crédito",
)
def crear_simulacion(entrada: SolicitudEntrada, caso_de_uso: CasoDeUso):
    return SimulacionSalida.desde_dominio(caso_de_uso.ejecutar(entrada.a_dominio()))


@app.get(
    "/simulaciones/{simulacion_id}",
    response_model=SimulacionSalida,
    tags=["Simulaciones"],
    summary="Consultar una simulación",
)
def consultar_simulacion(simulacion_id: str, caso_de_uso: CasoDeUso):
    simulacion = caso_de_uso.consultar(simulacion_id)
    if simulacion is None:
        raise HTTPException(status_code=404, detail="Simulación no encontrada")
    return SimulacionSalida.desde_dominio(simulacion)
