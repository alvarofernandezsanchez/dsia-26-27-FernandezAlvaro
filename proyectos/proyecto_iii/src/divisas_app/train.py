from pathlib import Path

import pandas as pd
from joblib import dump
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

FEATURES = [
    "rate",
    "rate_lag_1",
    "rate_lag_2",
    "rate_lag_3",
]


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prepara cotizaciones históricas para el modelo."""

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values(["base", "quote", "date"])

    grouped = df.groupby(["base", "quote"])["rate"]

    df["rate_lag_1"] = grouped.shift(1)
    df["rate_lag_2"] = grouped.shift(2)
    df["rate_lag_3"] = grouped.shift(3)

    # Cotización siguiente de cada par de divisas.
    df["target"] = grouped.shift(-1)

    df = df.dropna(
        subset=FEATURES + ["target"]
    ).copy()

    return df


def train_model(
    input_path: str = "datos/divisas.csv",
    model_path: str = "modelos/divisas_model.joblib",
) -> dict:
    """Entrena, evalúa y guarda un modelo sklearn."""

    df = pd.read_csv(input_path)
    df = prepare_data(df)

    if df.empty:
        raise ValueError("No hay suficientes datos para entrenar.")

    # División temporal global: 80 % entrenamiento, 20 % prueba.
    dates = sorted(df["date"].unique())
    if len(dates) < 5:
        raise ValueError("Se necesitan al menos cinco fechas distintas.")

    split_idx = int(len(dates) * 0.8)
    split_date = dates[split_idx]

    train_df = df[df["date"] < split_date]
    test_df = df[df["date"] >= split_date]

    if train_df.empty or test_df.empty:
        raise ValueError("La división temporal no produjo datos suficientes.")

    # Entrenamos un modelo independiente para cada par de divisas.
    models = {}
    predictions = []

    for (base, quote), group_train in train_df.groupby(["base", "quote"]):
        group_test = test_df[
            (test_df["base"] == base)
            & (test_df["quote"] == quote)
        ]

        if group_train.empty or group_test.empty:
            continue

        model = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            n_jobs=-1,
        )

        model.fit(
            group_train[FEATURES],
            group_train["target"],
        )

        y_pred = model.predict(group_test[FEATURES])

        models[(base, quote)] = model

        result = group_test[
            ["date", "base", "quote", "rate", "target"]
        ].copy()

        result["prediction"] = y_pred
        predictions.append(result)

    if not predictions:
        raise ValueError("No se pudieron evaluar los modelos.")

    results = pd.concat(predictions, ignore_index=True)

    mae = mean_absolute_error(
        results["target"],
        results["prediction"],
    )

    rmse = mean_squared_error(
        results["target"],
        results["prediction"],
    ) ** 0.5

    # Comparación con baseline: mañana = hoy.
    baseline_mae = mean_absolute_error(
        results["target"],
        results["rate"],
    )

    model_file = Path(model_path)
    model_file.parent.mkdir(parents=True, exist_ok=True)

    dump(
        {
            "models": models,
            "features": FEATURES,
        },
        model_file,
    )

    predictions_file = model_file.parent / "predicciones_test.csv"
    results.to_csv(predictions_file, index=False)

    metrics = {
        "mae": float(mae),
        "rmse": float(rmse),
        "baseline_mae": float(baseline_mae),
        "num_models": len(models),
        "train_rows": len(train_df),
        "test_rows": len(results),
    }

    metrics_file = model_file.parent / "metricas_modelo.csv"
    pd.DataFrame([metrics]).to_csv(metrics_file, index=False)

    return metrics


if __name__ == "__main__":
    metrics = train_model()

    print("Entrenamiento completado")
    for key, value in metrics.items():
        print(f"{key}: {value}")