from decimal import Decimal

from app.domain.modelos import SolicitudCredito
from app.domain.politicas import PoliticaCredito

POLITICA = PoliticaCredito()


def solicitud(**cambios):
    datos = dict(monto=Decimal("10000000"), plazo_meses=36, tasa_efectiva_anual=Decimal("0.24"))
    datos.update(cambios)
    return SolicitudCredito(**datos)


def test_solicitud_valida_se_aprueba():
    decision = POLITICA.evaluar(solicitud(), Decimal("380000"))
    assert decision.aprobada
    assert decision.motivos == ()


def test_monto_fuera_de_rango():
    decision = POLITICA.evaluar(solicitud(monto=Decimal("100000")), Decimal("10000"))
    assert not decision.aprobada
    assert "monto" in decision.motivos[0]


def test_plazo_fuera_de_rango():
    decision = POLITICA.evaluar(solicitud(plazo_meses=120), Decimal("200000"))
    assert not decision.aprobada
    assert "plazo" in decision.motivos[0]


def test_tasa_por_encima_del_maximo():
    decision = POLITICA.evaluar(solicitud(tasa_efectiva_anual=Decimal("0.35")), Decimal("400000"))
    assert not decision.aprobada
    assert "tasa" in decision.motivos[0]


def test_cuota_supera_capacidad_de_pago():
    decision = POLITICA.evaluar(solicitud(ingreso_mensual=Decimal("1000000")), Decimal("380000"))
    assert not decision.aprobada
    assert "ingreso" in decision.motivos[0]


def test_reune_todos_los_motivos():
    s = solicitud(monto=Decimal("1"), plazo_meses=1, tasa_efectiva_anual=Decimal("0.9"), ingreso_mensual=Decimal("10"))
    assert len(POLITICA.evaluar(s, Decimal("100")).motivos) == 4


def test_politica_configurable():
    estricta = PoliticaCredito(capacidad_maxima_pago=Decimal("0.10"))
    s = solicitud(ingreso_mensual=Decimal("3000000"))
    assert POLITICA.evaluar(s, Decimal("380000")).aprobada
    assert not estricta.evaluar(s, Decimal("380000")).aprobada
