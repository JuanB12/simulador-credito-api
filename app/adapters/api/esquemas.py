"""Contratos de entrada y salida de la API (Pydantic)."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.modelos import Simulacion, SolicitudCredito


class SolicitudEntrada(BaseModel):
    monto: Decimal = Field(gt=0, examples=[10000000], description="Monto solicitado en pesos")
    plazo_meses: int = Field(gt=0, le=360, examples=[36])
    tasa_efectiva_anual: Decimal = Field(ge=0, le=1, examples=[0.24], description="Tasa EA en decimal: 0.24 = 24%")
    ingreso_mensual: Decimal | None = Field(default=None, gt=0, examples=[3500000])

    def a_dominio(self) -> SolicitudCredito:
        return SolicitudCredito(**self.model_dump())


class CuotaSalida(BaseModel):
    numero: int
    cuota: Decimal
    interes: Decimal
    abono_capital: Decimal
    saldo: Decimal


class DecisionSalida(BaseModel):
    aprobada: bool
    motivos: list[str]


class SimulacionSalida(BaseModel):
    id: str
    creada_en: datetime
    monto: Decimal
    plazo_meses: int
    tasa_efectiva_anual: Decimal
    tasa_mensual: Decimal
    cuota_mensual: Decimal
    total_intereses: Decimal
    total_pagar: Decimal
    decision: DecisionSalida
    plan: list[CuotaSalida]

    @classmethod
    def desde_dominio(cls, s: Simulacion) -> "SimulacionSalida":
        return cls(
            id=s.id,
            creada_en=s.creada_en,
            monto=s.solicitud.monto,
            plazo_meses=s.solicitud.plazo_meses,
            tasa_efectiva_anual=s.solicitud.tasa_efectiva_anual,
            tasa_mensual=round(s.tasa_mensual, 8),
            cuota_mensual=s.cuota_mensual,
            total_intereses=s.total_intereses,
            total_pagar=s.total_pagar,
            decision=DecisionSalida(aprobada=s.decision.aprobada, motivos=list(s.decision.motivos)),
            plan=[CuotaSalida(**vars(c)) for c in s.plan],
        )
