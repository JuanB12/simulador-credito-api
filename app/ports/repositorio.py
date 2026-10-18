"""Puerto de salida: lo que el caso de uso necesita para guardar simulaciones.

El dominio solo conoce esta interfaz; las implementaciones viven en app/adapters.
"""

from typing import Protocol

from app.domain.modelos import Simulacion


class RepositorioSimulaciones(Protocol):
    def guardar(self, simulacion: Simulacion) -> None: ...

    def obtener(self, simulacion_id: str) -> Simulacion | None: ...
