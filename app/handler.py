"""Punto de entrada de AWS Lambda: Mangum traduce los eventos de API Gateway a ASGI."""

from mangum import Mangum

from app.adapters.api.main import app

handler = Mangum(app, lifespan="off")
