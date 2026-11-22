"""Pruebas de las métricas de ventas."""

from decimal import Decimal

from ventas_app.metrics import VentasMetrics
from ventas_app.validator import VentasValidator


def test_metricas_ventas():
    filas = [
        {
            "fecha": "2026-01-05",
            "region": "Norte",
            "producto": "Sensor A",
            "unidades": "12",
            "precio_unitario": "19.5",
            "cliente_id": "C001",
        },
        {
            "fecha": "2026-01-05",
            "region": "Sur",
            "producto": "Sensor B",
            "unidades": "4",
            "precio_unitario": "32.0",
            "cliente_id": "C002",
        },
        {
            "fecha": "2026-01-06",
            "region": "Norte",
            "producto": "Sensor A",
            "unidades": "7",
            "precio_unitario": "19.5",
            "cliente_id": "C003",
        },
    ]

    ventas = VentasValidator().validar(filas)
    metricas = VentasMetrics(ventas)

    assert metricas.importe_total() == Decimal("498.5")
    assert metricas.unidades_totales() == 23

    assert metricas.importe_por_region() == {
        "Norte": Decimal("370.5"),
        "Sur": Decimal("128"),
    }

    assert metricas.importe_por_producto() == {
        "Sensor A": Decimal("370.5"),
        "Sensor B": Decimal("128"),
    }


def test_metricas_sin_ventas():
    metricas = VentasMetrics([])

    assert metricas.importe_total() == Decimal("0")
    assert metricas.unidades_totales() == 0
    assert metricas.importe_por_region() == {}
    assert metricas.importe_por_producto() == {}