"""Adaptador en memoria: para desarrollo local y pruebas."""

from app.domain.modelos import Simulacion


class RepositorioEnMemoria:
    def __init__(self) -> None:
        self._datos: dict[str, Simulacion] = {}

    def guardar(self, simulacion: Simulacion) -> None:
        self._datos[simulacion.id] = simulacion

    def obtener(self, simulacion_id: str) -> Simulacion | None:
        return self._datos.get(simulacion_id)
