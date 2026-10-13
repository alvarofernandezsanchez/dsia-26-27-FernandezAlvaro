
import pytest
from pydantic import ValidationError

from divisas_app.contract import ExchangeRate


# Comprueba que un registro correcto supera la validación
def test_valid_exchange_rate():
    registro = ExchangeRate(
        date="2026-01-01",
        base="EUR",
        quote="USD",
        rate=1.15
    )

    assert registro.base == "EUR"
    assert registro.quote == "USD"
    assert registro.rate == 1.15


# Comprueba que no se aceptan tipos de cambio negativos
def test_negative_rate():
    with pytest.raises(ValidationError):
        ExchangeRate(
            date="2026-01-01",
            base="EUR",
            quote="USD",
            rate=-1
        )


# Comprueba que las monedas tienen tres letras mayúsculas
def test_invalid_currency():
    with pytest.raises(ValidationError):
        ExchangeRate(
            date="2026-01-01",
            base="EUR",
            quote="EURO",
            rate=1.15
        )


# Comprueba que la fecha tiene un formato válido
def test_invalid_date():
    with pytest.raises(ValidationError):
        ExchangeRate(
            date="fecha_incorrecta",
            base="EUR",
            quote="USD",
            rate=1.15
        )


# Comprueba que las monedas de origen y destino sean distintas
def test_same_currencies():
    with pytest.raises(ValidationError):
        ExchangeRate(
            date="2026-01-01",
            base="EUR",
            quote="EUR",
            rate=1.15
        )
