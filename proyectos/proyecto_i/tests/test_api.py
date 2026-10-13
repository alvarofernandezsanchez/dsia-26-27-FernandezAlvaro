
import pandas as pd
import requests
import pytest

from divisas_app.preprocess import ExchangeRatePreprocessor
from divisas_app.contract import DataLoadError


# Simula una respuesta correcta de Frankfurter
def test_update_from_api(tmp_path, monkeypatch):
    """Comprueba que se incorporan nuevas cotizaciones."""

    archivo = tmp_path / "divisas.csv"

    # Creamos un CSV histórico de prueba
    pd.DataFrame({
        "date": ["2026-01-01"],
        "base": ["EUR"],
        "quote": ["USD"],
        "rate": [1.10]
    }).to_csv(archivo, index=False)

    # Simulamos la respuesta de la API
    class FakeResponse:
        text = "date,base,quote,rate\n2026-01-02,EUR,USD,1.20\n"

        def raise_for_status(self):
            pass

    def fake_get(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(requests, "get", fake_get)

    processor = ExchangeRatePreprocessor(str(archivo))
    resultado = processor.update_from_api()

    assert len(resultado) == 2
    assert resultado["rate"].iloc[-1] == pytest.approx(1.20)


# Simula un fallo de conexión con la API
def test_api_connection_error(tmp_path, monkeypatch):
    """Comprueba que los fallos de conexión generan DataLoadError."""

    archivo = tmp_path / "divisas.csv"

    pd.DataFrame({
        "date": ["2026-01-01"],
        "base": ["EUR"],
        "quote": ["USD"],
        "rate": [1.10]
    }).to_csv(archivo, index=False)

    # Sustituimos requests.get por una función que provoca un error
    def fake_get(*args, **kwargs):
        raise requests.ConnectionError("Sin conexión")

    monkeypatch.setattr(requests, "get", fake_get)

    processor = ExchangeRatePreprocessor(str(archivo))

    with pytest.raises(DataLoadError):
        processor.update_from_api()


# Comprueba que no se modifica el histórico si no hay datos nuevos
def test_api_without_new_data(tmp_path, monkeypatch):
    """Conserva el CSV cuando la API devuelve una respuesta vacía."""

    archivo = tmp_path / "divisas.csv"

    # Creamos un histórico de prueba
    pd.DataFrame({
        "date": ["2026-01-01"],
        "base": ["EUR"],
        "quote": ["USD"],
        "rate": [1.10]
    }).to_csv(archivo, index=False)

    # Simulamos una respuesta vacía de Frankfurter
    class FakeResponse:
        text = ""

        def raise_for_status(self):
            pass

    def fake_get(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(requests, "get", fake_get)

    processor = ExchangeRatePreprocessor(str(archivo))
    resultado = processor.update_from_api()

    # El registro histórico debe seguir existiendo
    assert len(resultado) == 1

    # El archivo original debe conservar su contenido
    guardado = pd.read_csv(archivo)
    assert len(guardado) == 1
    assert guardado["rate"].iloc[0] == pytest.approx(1.10)
