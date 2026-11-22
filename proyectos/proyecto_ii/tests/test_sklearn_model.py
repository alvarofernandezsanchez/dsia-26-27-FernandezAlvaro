
import pandas as pd
import pytest
from joblib import load

from divisas_app.sklearn_inference import predict_next_rates
from divisas_app.train import prepare_data, train_model


@pytest.fixture
def sample_data(tmp_path):
    """Genera datos de prueba sin depender de archivos externos."""

    dates = pd.date_range("2023-01-01", periods=60)

    df = pd.DataFrame({
        "date": dates,
        "base": ["EUR"] * 60,
        "quote": ["USD"] * 60,
        "rate": [
            1.05 + i * 0.001 + (i % 5) * 0.0002
            for i in range(60)
        ],
    })

    csv_path = tmp_path / "divisas.csv"
    df.to_csv(csv_path, index=False)

    return df, csv_path


def test_prepare_data(sample_data):
    """Comprueba que se generan las variables históricas."""

    df, _ = sample_data
    prepared = prepare_data(df)

    assert "rate_lag_1" in prepared.columns
    assert "rate_lag_2" in prepared.columns
    assert "rate_lag_3" in prepared.columns
    assert "target" in prepared.columns
    assert not prepared.empty
    assert prepared["target"].notna().all()


def test_train_model(sample_data, tmp_path):
    """Comprueba el entrenamiento y guardado del modelo."""

    _, csv_path = sample_data
    model_path = tmp_path / "modelo.joblib"

    metrics = train_model(
        input_path=str(csv_path),
        model_path=str(model_path),
    )

    assert model_path.exists()
    assert metrics["num_models"] == 1
    assert metrics["mae"] >= 0
    assert metrics["rmse"] >= 0
    assert metrics["train_rows"] > 0
    assert metrics["test_rows"] > 0


def test_model_load(sample_data, tmp_path):
    """Comprueba que el modelo guardado puede cargarse."""

    _, csv_path = sample_data
    model_path = tmp_path / "modelo.joblib"

    train_model(
        input_path=str(csv_path),
        model_path=str(model_path),
    )

    artifact = load(model_path)

    assert ("EUR", "USD") in artifact["models"]
    assert len(artifact["features"]) == 4


@pytest.mark.integration
def test_sklearn_inference(sample_data, tmp_path):
    """Comprueba entrenamiento, carga e inferencia completos."""

    df, csv_path = sample_data
    model_path = tmp_path / "modelo.joblib"

    train_model(
        input_path=str(csv_path),
        model_path=str(model_path),
    )

    predictions = predict_next_rates(
        df,
        model_path=str(model_path),
    )

    assert len(predictions) == 1
    assert predictions.iloc[0]["base"] == "EUR"
    assert predictions.iloc[0]["quote"] == "USD"
    assert predictions.iloc[0]["predicted_next_rate"] > 0
