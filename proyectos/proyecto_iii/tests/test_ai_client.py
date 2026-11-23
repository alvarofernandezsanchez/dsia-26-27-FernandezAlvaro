
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

    with pytest.raises(ValueError, match="Falta la API key del proveedor openai"):
        client.generate_report(metrics)


# TEST 5: Simular una respuesta real de OpenAI
@patch("divisas_app.ai_client.OpenAI")
def test_real_report(mock_openai, metrics):
    # Simulamos la respuesta que devolvería OpenAI
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Informe financiero generado"

    mock_openai.return_value.chat.completions.create.return_value = mock_response

    config = AppConfig(
        ai_mode="real",
        openai_api_key="clave_de_prueba"
    )

    client = AIClient(config)
    report = client.generate_report(metrics)

    assert report == "Informe financiero generado"
    mock_openai.return_value.chat.completions.create.assert_called_once()

@patch("divisas_app.ai_client.OpenAI")
def test_nvidia_report(mock_openai, metrics):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Informe generado por NVIDIA"

    mock_openai.return_value.chat.completions.create.return_value = mock_response

    config = AppConfig(
        ai_mode="real",
        ai_provider="nvidia",
        nvidia_api_key="clave_ficticia",
        nvidia_model="nvidia/nemotron-3.5-super-vl-120b-a12b",
    )

    client = AIClient(config)
    report = client.generate_report(metrics)

    assert report == "Informe generado por NVIDIA"

    mock_openai.assert_called_once_with(
        api_key="clave_ficticia",
        base_url="https://integrate.api.nvidia.com/v1",
        timeout=30.0,
        max_retries=2,
    )

    mock_openai.return_value.chat.completions.create.assert_called_once()

    kwargs = mock_openai.return_value.chat.completions.create.call_args.kwargs

    assert kwargs["model"] == "nvidia/nemotron-3.5-super-vl-120b-a12b"

def test_nvidia_without_api_key(metrics):
        config = AppConfig(
            ai_mode="real",
            ai_provider="nvidia",
            nvidia_api_key="",
            nvidia_model="nvidia/nemotron-3.5-super-vl-120b-a12b",
        )

        client = AIClient(config)

        with pytest.raises(
            ValueError,
            match="Falta la API key del proveedor nvidia",
        ):
            client.generate_report(metrics)