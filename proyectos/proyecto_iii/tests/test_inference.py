
import pandas as pd
import pytest

from divisas_app.inference import ExchangeRateAnalyzer


# Comprueba que se calculan correctamente las estadísticas
def test_calculate_statistics():
    df = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-02"],
        "base": ["EUR", "EUR"],
        "quote": ["USD", "USD"],
        "rate": [1.10, 1.20]
    })

    analyzer = ExchangeRateAnalyzer(df)
    resultado = analyzer.calculate_statistics()

    assert resultado["mean_rate"].iloc[0] == pytest.approx(1.15)
    assert resultado["min_rate"].iloc[0] == 1.10
    assert resultado["max_rate"].iloc[0] == 1.20
    assert resultado["num_records"].iloc[0] == 2


# Comprueba la variación porcentual entre dos fechas
def test_calculate_variation():
    df = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-02"],
        "base": ["EUR", "EUR"],
        "quote": ["USD", "USD"],
        "rate": [1.10, 1.20]
    })

    analyzer = ExchangeRateAnalyzer(df)
    resultado = analyzer.calculate_variation()

    # (1.20 - 1.10) / 1.10 * 100 = 9.09 %
    assert resultado["variation_pct"].iloc[0] == pytest.approx(
        9.090909,
        rel=1e-5
    )


# Comprueba que el informe final contiene todas las métricas
def test_generate_report():
    df = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-02"],
        "base": ["EUR", "EUR"],
        "quote": ["USD", "USD"],
        "rate": [1.10, 1.20]
    })

    analyzer = ExchangeRateAnalyzer(df)
    report = analyzer.generate_report()

    assert len(report) == 1
    assert "mean_rate" in report.columns
    assert "variation_pct" in report.columns
