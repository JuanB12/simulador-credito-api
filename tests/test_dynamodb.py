from decimal import Decimal

import boto3
import pytest
from moto import mock_aws

from app.adapters.persistencia.dynamodb import RepositorioDynamoDB
from app.application.simular_credito import SimularCredito
from app.domain.modelos import SolicitudCredito


@pytest.fixture
def repositorio(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    with mock_aws():
        recurso = boto3.resource("dynamodb")
        recurso.create_table(
            TableName="simulaciones",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield RepositorioDynamoDB("simulaciones", recurso)


def test_guarda_y_recupera_la_misma_simulacion(repositorio):
    caso = SimularCredito(repositorio)
    original = caso.ejecutar(
        SolicitudCredito(Decimal("8000000"), 24, Decimal("0.22"), ingreso_mensual=Decimal("4000000"))
    )
    recuperada = repositorio.obtener(original.id)

    assert recuperada is not None
    assert recuperada.solicitud == original.solicitud
    assert recuperada.cuota_mensual == original.cuota_mensual
    assert recuperada.plan == original.plan
    assert recuperada.decision == original.decision


def test_id_inexistente(repositorio):
    assert repositorio.obtener("nada") is None
