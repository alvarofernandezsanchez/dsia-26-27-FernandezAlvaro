from pathlib import Path

import pandas as pd
from joblib import load

from divisas_app.train import FEATURES


def predict_next_rates(
    df: pd.DataFrame,
    model_path: str = "modelos/divisas_model.joblib",
) -> pd.DataFrame:
    """Predice la siguiente cotización disponible de cada par."""

    if not Path(model_path).exists():
        raise FileNotFoundError(
            f"No se encuentra el modelo: {model_path}"
        )

    artifact = load(model_path)
    models = artifact["models"]

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["base", "quote", "date"])

    grouped = df.groupby(["base", "quote"])["rate"]

    df["rate_lag_1"] = grouped.shift(1)
    df["rate_lag_2"] = grouped.shift(2)
    df["rate_lag_3"] = grouped.shift(3)

    latest = df.groupby(["base", "quote"]).tail(1)
    latest = latest.dropna(subset=FEATURES)

    predictions = []

    for _, row in latest.iterrows():
        pair = (row["base"], row["quote"])

        if pair not in models:
            continue

        features = pd.DataFrame(
            [{feature: row[feature] for feature in FEATURES}]
        )

        prediction = float(models[pair].predict(features)[0])

        predictions.append(
            {
                "date": row["date"].strftime("%Y-%m-%d"),
                "base": row["base"],
                "quote": row["quote"],
                "last_rate": float(row["rate"]),
                "predicted_next_rate": prediction,
            }
        )

    return pd.DataFrame(
        predictions,
        columns=[
            "date",
            "base",
            "quote",
            "last_rate",
            "predicted_next_rate",
        ],
    )