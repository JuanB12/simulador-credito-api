"""Políticas de crédito: reglas de negocio que deciden si una solicitud es viable."""

from dataclasses import dataclass
from decimal import Decimal

from app.domain.modelos import Decision, SolicitudCredito


@dataclass(frozen=True)
class PoliticaCredito:
    monto_minimo: Decimal = Decimal("500000")
    monto_maximo: Decimal = Decimal("200000000")
    plazo_minimo: int = 6
    plazo_maximo: int = 84
    tasa_maxima_ea: Decimal = Decimal("0.30")
    # La cuota no debería comprometer más de este porcentaje del ingreso mensual
    capacidad_maxima_pago: Decimal = Decimal("0.30")

    def evaluar(self, solicitud: SolicitudCredito, cuota_mensual: Decimal) -> Decision:
        motivos = []
        if not self.monto_minimo <= solicitud.monto <= self.monto_maximo:
            motivos.append(f"El monto debe estar entre {self.monto_minimo:,.0f} y {self.monto_maximo:,.0f}")
        if not self.plazo_minimo <= solicitud.plazo_meses <= self.plazo_maximo:
            motivos.append(f"El plazo debe estar entre {self.plazo_minimo} y {self.plazo_maximo} meses")
        if solicitud.tasa_efectiva_anual > self.tasa_maxima_ea:
            motivos.append(f"La tasa supera el máximo permitido ({self.tasa_maxima_ea:.0%} EA)")
        if solicitud.ingreso_mensual is not None:
            limite = solicitud.ingreso_mensual * self.capacidad_maxima_pago
            if cuota_mensual > limite:
                motivos.append(
                    f"La cuota supera el {self.capacidad_maxima_pago:.0%} del ingreso mensual "
                    f"(máximo {limite:,.0f})"
                )
        return Decision(aprobada=not motivos, motivos=tuple(motivos))
