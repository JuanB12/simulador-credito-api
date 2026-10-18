"""Caso de uso: simular un crédito y decidir si cumple la política."""

from app.domain.amortizacion import plan_de_pagos, tasa_mensual_desde_efectiva_anual
from app.domain.modelos import Simulacion, SolicitudCredito
from app.domain.politicas import PoliticaCredito
from app.ports.repositorio import RepositorioSimulaciones


class SimularCredito:
    def __init__(self, repositorio: RepositorioSimulaciones, politica: PoliticaCredito | None = None):
        self._repositorio = repositorio
        self._politica = politica or PoliticaCredito()

    def ejecutar(self, solicitud: SolicitudCredito) -> Simulacion:
        tasa_mensual = tasa_mensual_desde_efectiva_anual(solicitud.tasa_efectiva_anual)
        plan = plan_de_pagos(solicitud.monto, tasa_mensual, solicitud.plazo_meses)
        cuota_mensual = plan[0].cuota
        simulacion = Simulacion(
            solicitud=solicitud,
            tasa_mensual=tasa_mensual,
            cuota_mensual=cuota_mensual,
            plan=plan,
            decision=self._politica.evaluar(solicitud, cuota_mensual),
        )
        self._repositorio.guardar(simulacion)
        return simulacion

    def consultar(self, simulacion_id: str) -> Simulacion | None:
        return self._repositorio.obtener(simulacion_id)
