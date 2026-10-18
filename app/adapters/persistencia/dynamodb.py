"""Adaptador de DynamoDB: persistencia en AWS.

Guarda la solicitud y el resultado; el plan de pagos se recalcula al consultar,
porque es determinístico y así cada ítem ocupa muy poco espacio.
"""

from datetime import datetime
from decimal import Decimal

import boto3

from app.domain.amortizacion import plan_de_pagos
from app.domain.modelos import Decision, Simulacion, SolicitudCredito


class RepositorioDynamoDB:
    def __init__(self, nombre_tabla: str, cliente=None) -> None:
        recurso = cliente or boto3.resource("dynamodb")
        self._tabla = recurso.Table(nombre_tabla)

    def guardar(self, simulacion: Simulacion) -> None:
        s = simulacion.solicitud
        item = {
            "id": simulacion.id,
            "creada_en": simulacion.creada_en.isoformat(),
            "monto": s.monto,
            "plazo_meses": s.plazo_meses,
            "tasa_efectiva_anual": s.tasa_efectiva_anual,
            "tasa_mensual": simulacion.tasa_mensual,
            "cuota_mensual": simulacion.cuota_mensual,
            "aprobada": simulacion.decision.aprobada,
            "motivos": list(simulacion.decision.motivos),
        }
        if s.ingreso_mensual is not None:
            item["ingreso_mensual"] = s.ingreso_mensual
        self._tabla.put_item(Item=item)

    def obtener(self, simulacion_id: str) -> Simulacion | None:
        item = self._tabla.get_item(Key={"id": simulacion_id}).get("Item")
        if not item:
            return None
        solicitud = SolicitudCredito(
            monto=Decimal(item["monto"]),
            plazo_meses=int(item["plazo_meses"]),
            tasa_efectiva_anual=Decimal(item["tasa_efectiva_anual"]),
            ingreso_mensual=Decimal(item["ingreso_mensual"]) if "ingreso_mensual" in item else None,
        )
        tasa_mensual = Decimal(item["tasa_mensual"])
        return Simulacion(
            id=item["id"],
            creada_en=datetime.fromisoformat(item["creada_en"]),
            solicitud=solicitud,
            tasa_mensual=tasa_mensual,
            cuota_mensual=Decimal(item["cuota_mensual"]),
            plan=plan_de_pagos(solicitud.monto, tasa_mensual, solicitud.plazo_meses),
            decision=Decision(aprobada=bool(item["aprobada"]), motivos=tuple(item.get("motivos", []))),
        )
