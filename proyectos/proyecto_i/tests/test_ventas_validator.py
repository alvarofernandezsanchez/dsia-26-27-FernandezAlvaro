"""Pruebas de validación de ventas."""

import pytest

from ventas_app.validator import (
    ErrorValidacionVentas,
    VentasValidator,
)


@pytest.fixture
def venta_valida():
    """Devuelve una fila de venta correcta."""
    return {
        "fecha": "2026-01-05",
        "region": "Norte",
        "producto": "Sensor A",
        "unidades": "12",
        "precio_unitario": "19.5",
        "cliente_id": "C001",
    }


def test_venta_valida(venta_valida):
    venta = VentasValidator().validar_fila(venta_valida, 2)

    assert venta.region == "Norte"
    assert venta.producto == "Sensor A"
    assert venta.unidades == 12


@pytest.mark.parametrize(
    "campo,valor",
    [
        ("fecha", ""),
        ("region", ""),
        ("producto", ""),
        ("unidades", ""),
        ("precio_unitario", ""),
        ("cliente_id", ""),
        ("unidades", "-3"),
        ("unidades", "abc"),
        ("precio_unitario", "-10"),
        ("precio_unitario", "abc"),
        ("fecha", "2026-99-99"),
    ],
)
def test_ventas_invalidas(venta_valida, campo, valor):
    fila = venta_valida.copy()
    fila[campo] = valor

    with pytest.raises(ErrorValidacionVentas):
        VentasValidator().validar_fila(fila, 2)