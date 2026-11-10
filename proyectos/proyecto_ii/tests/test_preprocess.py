
import pandas as pd
import pytest

from divisas_app.preprocess import ExchangeRatePreprocessor
from divisas_app.contract import DataLoadError


# Comprueba que podemos cargar un CSV correctamente
def test_load_data(tmp_path):
    archivo = tmp_path / "divisas.csv"

    df = pd.DataFrame({
        "date": ["2026-01-01"],
        "base": ["EUR"],
        "quote": ["USD"],
        "rate": [1.15]
    })

    df.to_csv(archivo, index=False)

    processor = ExchangeRatePreprocessor(str(archivo))
    resultado = processor.load_data()

    assert len(resultado) == 1
    assert list(resultado.columns) == ["date", "base", "quote", "rate"]


# Comprueba que se detecta un archivo inexistente
def test_missing_file(tmp_path):
    archivo = tmp_path / "no_existe.csv"

    processor = ExchangeRatePreprocessor(str(archivo))

    with pytest.raises(DataLoadError):
        processor.load_data()


# Comprueba que los registros inválidos se separan correctamente
def test_validate_data():
    df = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-02"],
        "base": ["EUR", "EUR"],
        "quote": ["USD", "GBP"],
        "rate": [1.15, -2.0]
    })

    processor = ExchangeRatePreprocessor("datos/divisas.csv")

    validos, invalidos = processor.validate_data(df)

    assert len(validos) == 1
    assert len(invalidos) == 1


# Comprueba que se detectan cotizaciones duplicadas
def test_remove_duplicates():
    df = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-01"],
        "base": ["EUR", "EUR"],
        "quote": ["USD", "USD"],
        "rate": [1.15, 1.15]
    })

    processor = ExchangeRatePreprocessor("datos/divisas.csv")

    limpios, duplicados = processor.remove_duplicates(df)

    assert len(limpios) == 1
    assert len(duplicados) == 1
