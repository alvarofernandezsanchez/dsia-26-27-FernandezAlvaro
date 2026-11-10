
import pandas as pd
from pydantic import ValidationError as PydanticValidationError

from .contract import ExchangeRate, DataLoadError

import requests
from io import StringIO

#cargar, validar y limpiar el dataset
class ExchangeRatePreprocessor:

    def __init__(self, filepath: str):
        """Guarda la ruta del archivo CSV que vamos a procesar."""
        self.filepath = filepath

    def load_data(self) -> pd.DataFrame:
        """Carga el CSV y comprueba que contiene las columnas necesarias."""
        try:
            df = pd.read_csv(self.filepath)
        except (OSError, pd.errors.ParserError) as error:
            raise DataLoadError(f"No se pudo cargar el archivo: {error}") from error

        required_columns = {"date", "base", "quote", "rate"}

        if not required_columns.issubset(df.columns):
            raise DataLoadError(
                "El CSV no contiene todas las columnas necesarias"
            )

        return df

    def validate_data(self, df: pd.DataFrame):
        """Separa los registros válidos de los que contienen errores."""
        valid_records = []
        invalid_records = []

        for index, row in df.iterrows():
            try:
                # Pydantic comprueba cada campo usando contract.py
                record = ExchangeRate.model_validate(row.to_dict())
                valid_records.append(record.model_dump(mode="json"))

            except PydanticValidationError as error:
                # Guardamos la fila incorrecta y el motivo del error
                invalid_record = row.to_dict()
                invalid_record["error"] = str(error)
                invalid_record["row_number"] = index + 2
                invalid_records.append(invalid_record)

        valid_df = pd.DataFrame(
            valid_records,
            columns=["date", "base", "quote", "rate"]
        )
        invalid_df = pd.DataFrame(invalid_records)

        return valid_df, invalid_df

    def remove_duplicates(self, df: pd.DataFrame):
        """Elimina cotizaciones repetidas y conserva los duplicados."""
        columns = ["date", "base", "quote"]

        # Una fecha y un par de monedas deben tener una sola cotización
        duplicates = df.duplicated(subset=columns, keep="first")

        clean_df = df.loc[~duplicates].copy()
        duplicate_df = df.loc[duplicates].copy()

        return clean_df, duplicate_df

    
    def update_from_api(self) -> pd.DataFrame:
        """Descarga cotizaciones nuevas y actualiza el CSV sin duplicados."""

        # Leemos los datos históricos que ya tenemos
        df_actual = self.load_data()

        # Buscamos la última fecha disponible en nuestro CSV
        ultima_fecha = pd.to_datetime(df_actual["date"]).max()

        # Solicitamos cotizaciones desde el día siguiente
        fecha_inicio = (
            ultima_fecha + pd.Timedelta(days=1)
        ).strftime("%Y-%m-%d")

        # Conservamos las mismas monedas que tiene el dataset
        monedas = sorted(df_actual["quote"].unique())

        # Consultamos los datos nuevos en formato CSV
        url = "https://api.frankfurter.dev/v2/rates.csv"

        try:
            response = requests.get(
                url,
                params={
                    "from": fecha_inicio,
                    "base": "EUR",
                    "quotes": ",".join(monedas)
                },
                timeout=30
            )
            response.raise_for_status()

            # Si la API no devuelve cotizaciones, conservamos el histórico
            if not response.text.strip():
                print("No hay cotizaciones nuevas disponibles.")
                return df_actual

            # Convertimos la respuesta de la API en un DataFrame
            nuevos = pd.read_csv(StringIO(response.text))

        except (requests.RequestException, pd.errors.ParserError) as error:
            raise DataLoadError(
                f"Error al actualizar desde Frankfurter: {error}"
            ) from error

        # Comprobamos que la API devuelve las columnas esperadas
        columnas = {"date", "base", "quote", "rate"}

        if not columnas.issubset(nuevos.columns):
            raise DataLoadError(
                "La API no devolvió las columnas necesarias"
            )

        # Combinamos el histórico con las cotizaciones nuevas
        actualizado = pd.concat(
            [df_actual, nuevos],
            ignore_index=True
        )

        # Validamos los registros antes de guardar el CSV
        validos, invalidos = self.validate_data(actualizado)

        if not invalidos.empty:
            raise DataLoadError(
                f"La actualización contiene {len(invalidos)} registros inválidos"
            )

        # Eliminamos posibles cotizaciones repetidas
        actualizado, duplicados = self.remove_duplicates(validos)

        # Guardamos los datos actualizados
        actualizado.to_csv(self.filepath, index=False)

        return actualizado

