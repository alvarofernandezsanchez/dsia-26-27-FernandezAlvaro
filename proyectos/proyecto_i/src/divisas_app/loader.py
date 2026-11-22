"""Carga de datos de divisas desde archivos CSV."""

from pathlib import Path

import pandas as pd

from .contract import DataLoadError


class ExchangeRateLoader:
    """Carga cotizaciones desde un archivo CSV."""

    REQUIRED_COLUMNS = {"date", "base", "quote", "rate"}

    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)

    def load_data(self) -> pd.DataFrame:
        """Carga el CSV y comprueba las columnas obligatorias."""

        try:
            df = pd.read_csv(self.filepath)

        except (
            OSError,
            UnicodeError,
            pd.errors.ParserError,
            pd.errors.EmptyDataError,
        ) as error:
            raise DataLoadError(
                f"No se pudo cargar el archivo: {error}"
            ) from error

        if not self.REQUIRED_COLUMNS.issubset(df.columns):
            missing = self.REQUIRED_COLUMNS - set(df.columns)

            raise DataLoadError(
                f"Faltan columnas obligatorias: {sorted(missing)}"
            )

        return df