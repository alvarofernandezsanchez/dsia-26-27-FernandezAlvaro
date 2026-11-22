"""Cálculo de métricas de negocio a partir de ventas validadas."""

from collections import defaultdict
from decimal import Decimal

from .validator import Venta


class VentasMetrics:
    """Calcula importes y agrupaciones de ventas."""

    def __init__(self, ventas: list[Venta]):
        self.ventas = ventas

    def importe_total(self) -> Decimal:
        """Calcula el importe total de todas las ventas."""
        return sum(
            (
                venta.unidades * venta.precio_unitario
                for venta in self.ventas
            ),
            Decimal("0"),
        )

    def importe_por_region(self) -> dict[str, Decimal]:
        """Calcula el importe vendido en cada región."""
        resultados = defaultdict(lambda: Decimal("0"))

        for venta in self.ventas:
            resultados[venta.region] += (
                venta.unidades * venta.precio_unitario
            )

        return dict(sorted(resultados.items()))

    def importe_por_producto(self) -> dict[str, Decimal]:
        """Calcula el importe vendido por cada producto."""
        resultados = defaultdict(lambda: Decimal("0"))

        for venta in self.ventas:
            resultados[venta.producto] += (
                venta.unidades * venta.precio_unitario
            )

        return dict(sorted(resultados.items()))

    def unidades_totales(self) -> int:
        """Calcula el número total de unidades vendidas."""
        return sum(venta.unidades for venta in self.ventas)