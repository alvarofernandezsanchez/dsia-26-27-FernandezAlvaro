"""Cálculo de métricas y estadísticas de tipos de cambio."""

import pandas as pd


class ExchangeRateMetrics:
    """Calcula estadísticas de las cotizaciones validadas."""

    def __init__(self, df: pd.DataFrame):
        """Recibe los datos limpios que vamos a analizar."""
        self.df = df.copy()

    def calculate_statistics(self) -> pd.DataFrame:
        """Calcula media, mínimo, máximo y número de registros."""

        statistics = self.df.groupby(["base", "quote"])["rate"].agg(
            mean_rate="mean",
            min_rate="min",
            max_rate="max",
            num_records="count",
        )

        return statistics.reset_index()

    def calculate_variation(self) -> pd.DataFrame:
        """Calcula la variación porcentual entre primera y última fecha."""

        df_sorted = self.df.sort_values("date")

        grouped = df_sorted.groupby(["base", "quote"])["rate"]

        first_rate = grouped.first()
        last_rate = grouped.last()

        variation = ((last_rate - first_rate) / first_rate) * 100

        return variation.reset_index(name="variation_pct")

    def generate_report(self) -> pd.DataFrame:
        """Combina todas las estadísticas en un informe."""

        statistics = self.calculate_statistics()
        variation = self.calculate_variation()

        return statistics.merge(
            variation,
            on=["base", "quote"],
            how="left",
        )