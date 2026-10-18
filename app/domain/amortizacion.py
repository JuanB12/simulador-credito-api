"""Sistema de amortización francés: cuota fija mensual.

Todos los cálculos usan Decimal para no perder precisión con dinero.
"""

from decimal import ROUND_HALF_UP, Decimal, getcontext

from app.domain.modelos import Cuota

getcontext().prec = 28
CENTAVO = Decimal("0.01")


def redondear(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVO, rounding=ROUND_HALF_UP)


def tasa_mensual_desde_efectiva_anual(tasa_ea: Decimal) -> Decimal:
    """Convierte una tasa efectiva anual en su equivalente mensual: (1 + EA)^(1/12) - 1."""
    if tasa_ea < 0:
        raise ValueError("La tasa efectiva anual no puede ser negativa")
    return (Decimal(1) + tasa_ea) ** (Decimal(1) / Decimal(12)) - Decimal(1)


def cuota_fija(monto: Decimal, tasa_mensual: Decimal, plazo_meses: int) -> Decimal:
    """Cuota constante: P · i / (1 - (1 + i)^-n). Con tasa 0 es simplemente P / n."""
    if monto <= 0:
        raise ValueError("El monto debe ser mayor que cero")
    if plazo_meses <= 0:
        raise ValueError("El plazo debe ser mayor que cero")
    if tasa_mensual == 0:
        return redondear(monto / plazo_meses)
    factor = (Decimal(1) + tasa_mensual) ** -plazo_meses
    return redondear(monto * tasa_mensual / (Decimal(1) - factor))


def plan_de_pagos(monto: Decimal, tasa_mensual: Decimal, plazo_meses: int) -> tuple[Cuota, ...]:
    """Genera la tabla de amortización. La última cuota absorbe los centavos del redondeo
    para que el saldo final quede exactamente en cero."""
    cuota = cuota_fija(monto, tasa_mensual, plazo_meses)
    saldo = monto
    plan = []
    for numero in range(1, plazo_meses + 1):
        interes = redondear(saldo * tasa_mensual)
        if numero == plazo_meses:
            abono = saldo
            cuota_periodo = abono + interes
        else:
            abono = cuota - interes
            cuota_periodo = cuota
        saldo = saldo - abono
        plan.append(Cuota(numero, cuota_periodo, interes, abono, saldo))
    return tuple(plan)
