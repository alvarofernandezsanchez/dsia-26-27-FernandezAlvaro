
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from divisas_app.ai_client import AIClient
from divisas_app.config import AppConfig


# Creamos unas métricas de ejemplo para los tests
@pytest.fixture
def metrics():
    """Devuelve datos de prueba de una divisa."""
    return pd.DataFrame([
        {
            "base": "EUR",
            "quote": "USD",
            "mean_rate": 1.15,
            "variation_pct": 8.5
        }
    ])


# TEST 1: Comprobar que el modo mock genera un informe
def test_mock_report(metrics):
    config = AppConfig(ai_mode="mock")
    client = AIClient(config)

    report = client.generate_report(metrics)

    assert "EUR/USD" in report
    assert "1.1500" in report
    assert "8.50%" in report


# TEST 2: Comprobar que se rechazan métricas vacías
def test_empty_metrics():
    config = AppConfig(ai_mode="mock")
    client = AIClient(config)

    with pytest.raises(ValueError, match="No hay métricas"):
        client.generate_report(pd.DataFrame())


# TEST 3: Comprobar que se rechaza un modo incorrecto
def test_invalid_mode(metrics):
    config = AppConfig(ai_mode="incorrecto")
    client = AIClient(config)

    with pytest.raises(ValueError, match="Modo de IA no válido"):
        client.generate_report(metrics)


# TEST 4: Comprobar que el modo real exige una API key
def test_real_without_api_key(metrics):
    config = AppConfig(ai_mode="real", openai_api_key="")
    client = AIClient(config)

    with pytest.raises(ValueError, match="Falta OPENAI_API_KEY"):
        client.generate_report(metrics)


# TEST 5: Simular una respuesta real de OpenAI
@patch("divisas_app.ai_client.OpenAI")
def test_real_report(mock_openai, metrics):
    # Simulamos la respuesta que devolvería OpenAI
    mock_response = MagicMock()
    mock_response.output_text = "Informe financiero generado"

    mock_openai.return_value.responses.create.return_value = mock_response

    config = AppConfig(
        ai_mode="real",
        openai_api_key="clave_de_prueba"
    )

    client = AIClient(config)
    report = client.generate_report(metrics)

    assert report == "Informe financiero generado"
    mock_openai.return_value.responses.create.assert_called_once()
