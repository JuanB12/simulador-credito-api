from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.adapters.api.main import app, obtener_repositorio
from app.adapters.persistencia.memoria import RepositorioEnMemoria


@pytest.fixture
def cliente():
    repositorio = RepositorioEnMemoria()
    app.dependency_overrides[obtener_repositorio] = lambda: repositorio
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_salud(cliente):
    assert cliente.get("/salud").json() == {"estado": "ok"}


def test_crear_y_consultar_simulacion(cliente):
    cuerpo = {"monto": 10000000, "plazo_meses": 36, "tasa_efectiva_anual": 0.24, "ingreso_mensual": 3500000}
    creada = cliente.post("/simulaciones", json=cuerpo)
    assert creada.status_code == 201
    datos = creada.json()
    assert datos["decision"]["aprobada"] is True
    assert len(datos["plan"]) == 36
    assert Decimal(datos["plan"][-1]["saldo"]) == 0
    assert Decimal(datos["total_pagar"]) == Decimal(datos["monto"]) + Decimal(datos["total_intereses"])

    consultada = cliente.get(f"/simulaciones/{datos['id']}")
    assert consultada.status_code == 200
    assert consultada.json()["cuota_mensual"] == datos["cuota_mensual"]


def test_simulacion_rechazada_explica_motivos(cliente):
    cuerpo = {"monto": 10000000, "plazo_meses": 36, "tasa_efectiva_anual": 0.24, "ingreso_mensual": 800000}
    datos = cliente.post("/simulaciones", json=cuerpo).json()
    assert datos["decision"]["aprobada"] is False
    assert datos["decision"]["motivos"]


def test_simulacion_inexistente(cliente):
    assert cliente.get("/simulaciones/no-existe").status_code == 404


@pytest.mark.parametrize(
    "cuerpo",
    [
        {"monto": -1, "plazo_meses": 12, "tasa_efectiva_anual": 0.2},
        {"monto": 1000000, "plazo_meses": 0, "tasa_efectiva_anual": 0.2},
        {"monto": 1000000, "plazo_meses": 12, "tasa_efectiva_anual": 2},
        {"plazo_meses": 12, "tasa_efectiva_anual": 0.2},
    ],
)
def test_validacion_de_entrada(cliente, cuerpo):
    assert cliente.post("/simulaciones", json=cuerpo).status_code == 422
