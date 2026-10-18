"""Entidades del dominio. No dependen de FastAPI, AWS ni de ninguna librería externa."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4


@dataclass(frozen=True)
class SolicitudCredito:
    monto: Decimal
    plazo_meses: int
    tasa_efectiva_anual: Decimal
    ingreso_mensual: Decimal | None = None


@dataclass(frozen=True)
class Cuota:
    numero: int
    cuota: Decimal
    interes: Decimal
    abono_capital: Decimal
    saldo: Decimal


@dataclass(frozen=True)
class Decision:
    aprobada: bool
    motivos: tuple[str, ...] = ()


@dataclass(frozen=True)
class Simulacion:
    solicitud: SolicitudCredito
    tasa_mensual: Decimal
    cuota_mensual: Decimal
    plan: tuple[Cuota, ...]
    decision: Decision
    id: str = field(default_factory=lambda: uuid4().hex)
    creada_en: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def total_intereses(self) -> Decimal:
        return sum((c.interes for c in self.plan), Decimal("0"))

    @property
    def total_pagar(self) -> Decimal:
        return sum((c.cuota for c in self.plan), Decimal("0"))
