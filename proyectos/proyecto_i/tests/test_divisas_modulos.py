"""Tests de los nuevos módulos de divisas."""

import pandas as pd
import pytest

from divisas_app.contract import DataLoadError
from divisas_app.loader import ExchangeRateLoader
from divisas_app.validator import ExchangeRateValidator
from divisas_app.metrics import ExchangeRateMetrics


def test_loader_csv_valido(tmp_path):
    archivo = tmp_path / "divisas.csv"
    archivo.write_text(
        "date,base,quote,rate\n"
        "2026-01-01,EUR,USD,1.10\n",
        encoding="utf-8",
    )

    df = ExchangeRateLoader(archivo).load_data()

    assert len(df) == 1
    assert df.iloc[0]["rate"] == pytest.approx(1.10)


@pytest.mark.parametrize(
    "contenido",
    [
        "",
        "date,base,quote\n2026-01-01,EUR,USD\n",
    ],
)
def test_loader_csv_invalido(tmp_path, contenido):
    archivo = tmp_path / "divisas.csv"
    archivo.write_text(contenido, encoding="utf-8")

    with pytest.raises(DataLoadError):
        ExchangeRateLoader(archivo).load_data()


@pytest.mark.parametrize(
    "base,quote,rate",
    [
        ("EUR", "USD", -1.0),
        ("eur", "USD", 1.10),
        ("EUR", "EUR", 1.10),
        ("EUR", "USD", 0),
    ],
)
def test_validator_registros_invalidos(base, quote, rate):
    df = pd.DataFrame(
        [{
            "date": "2026-01-01",
            "base": base,
            "quote": quote,
            "rate": rate,
        }]
    )

    validos, invalidos = ExchangeRateValidator().validate_data(df)

    assert len(validos) == 0
    assert len(invalidos) == 1


def test_validator_duplicados():
    df = pd.DataFrame(
        [
            {"date": "2026-01-01", "base": "EUR", "quote": "USD", "rate": 1.10},
            {"date": "2026-01-01", "base": "EUR", "quote": "USD", "rate": 1.20},
        ]
    )

    limpios, duplicados = ExchangeRateValidator().remove_duplicates(df)

    assert len(limpios) == 1
    assert len(duplicados) == 1
    assert limpios.iloc[0]["rate"] == pytest.approx(1.10)


def test_metricas_divisas():
    df = pd.DataFrame(
        [
            {"date": "2026-01-01", "base": "EUR", "quote": "USD", "rate": 1.0},
            {"date": "2026-01-02", "base": "EUR", "quote": "USD", "rate": 1.2},
        ]
    )

    metricas = ExchangeRateMetrics(df)

    estadisticas = metricas.calculate_statistics()
    variacion = metricas.calculate_variation()
    informe = metricas.generate_report()

    assert estadisticas.iloc[0]["mean_rate"] == pytest.approx(1.1)
    assert estadisticas.iloc[0]["min_rate"] == pytest.approx(1.0)
    assert estadisticas.iloc[0]["max_rate"] == pytest.approx(1.2)
    assert estadisticas.iloc[0]["num_records"] == 2
    assert variacion.iloc[0]["variation_pct"] == pytest.approx(20.0)
    assert len(informe) == 1