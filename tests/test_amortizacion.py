from decimal import Decimal

import pytest

from app.domain.amortizacion import cuota_fija, plan_de_pagos, tasa_mensual_desde_efectiva_anual

MONTO = Decimal("10000000")


def test_tasa_mensual_equivalente_a_efectiva_anual():
    tasa = tasa_mensual_desde_efectiva_anual(Decimal("0.24"))
    # Capitalizar la tasa mensual 12 veces debe devolver la EA original
    assert (1 + tasa) ** 12 - 1 == pytest.approx(Decimal("0.24"), abs=Decimal("1e-20"))
    assert round(tasa, 6) == Decimal("0.018088")


def test_cuota_fija_coincide_con_la_formula():
    i = float(tasa_mensual_desde_efectiva_anual(Decimal("0.24")))
    esperada = 10_000_000 * i / (1 - (1 + i) ** -36)
    assert float(cuota_fija(MONTO, Decimal(str(i)), 36)) == pytest.approx(esperada, abs=0.01)


def test_con_tasa_cero_la_cuota_es_monto_sobre_plazo():
    assert cuota_fija(Decimal("1200000"), Decimal("0"), 12) == Decimal("100000.00")


@pytest.mark.parametrize("plazo", [6, 12, 36, 84])
def test_plan_deja_saldo_en_cero_y_abona_todo_el_capital(plazo):
    tasa = tasa_mensual_desde_efectiva_anual(Decimal("0.26"))
    plan = plan_de_pagos(MONTO, tasa, plazo)
    assert len(plan) == plazo
    assert plan[-1].saldo == Decimal("0")
    assert sum(c.abono_capital for c in plan) == MONTO


def test_cada_cuota_es_interes_mas_abono():
    plan = plan_de_pagos(MONTO, tasa_mensual_desde_efectiva_anual(Decimal("0.2")), 24)
    for c in plan:
        assert c.cuota == c.interes + c.abono_capital


def test_interes_decrece_y_abono_crece():
    plan = plan_de_pagos(MONTO, tasa_mensual_desde_efectiva_anual(Decimal("0.2")), 24)
    intereses = [c.interes for c in plan]
    abonos = [c.abono_capital for c in plan[:-1]]
    assert intereses == sorted(intereses, reverse=True)
    assert abonos == sorted(abonos)


@pytest.mark.parametrize("monto,plazo", [(Decimal("0"), 12), (Decimal("-5"), 12), (MONTO, 0)])
def test_valores_invalidos(monto, plazo):
    with pytest.raises(ValueError):
        cuota_fija(monto, Decimal("0.01"), plazo)


def test_tasa_negativa_no_permitida():
    with pytest.raises(ValueError):
        tasa_mensual_desde_efectiva_anual(Decimal("-0.1"))
