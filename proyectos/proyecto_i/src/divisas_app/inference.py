
import pandas as pd


# Clase encargada de calcular estadísticas de los tipos de cambio
class ExchangeRateAnalyzer:

    def __init__(self, df: pd.DataFrame):
        """Guarda los datos limpios que vamos a analizar."""
        self.df = df.copy()

    def calculate_statistics(self) -> pd.DataFrame:
        """Calcula media, mínimo y máximo para cada divisa."""

        # Agrupamos los registros por moneda de origen y destino
        statistics = self.df.groupby(["base", "quote"])["rate"].agg(
            mean_rate="mean",
            min_rate="min",
            max_rate="max",
            num_records="count"
        )

        return statistics.reset_index()

    def calculate_variation(self) -> pd.DataFrame:
        """Calcula la variación porcentual entre la primera y última fecha."""

        # Ordenamos por fecha para identificar la primera y última cotización
        df_sorted = self.df.sort_values("date")

        # Agrupamos las cotizaciones por cada par de monedas
        grouped = df_sorted.groupby(["base", "quote"])["rate"]

        first_rate = grouped.first()
        last_rate = grouped.last()

        # Fórmula: ((valor final - valor inicial) / valor inicial) * 100
        variation = ((last_rate - first_rate) / first_rate) * 100

        return variation.reset_index(name="variation_pct")

    def generate_report(self) -> pd.DataFrame:
        """Combina las estadísticas y variaciones en un único informe."""

        statistics = self.calculate_statistics()
        variation = self.calculate_variation()

        # Unimos los resultados utilizando las monedas como identificadores
        report = statistics.merge(
            variation,
            on=["base", "quote"],
            how="left"
        )

        return report
