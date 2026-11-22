"""Validación y eliminación de duplicados en cotizaciones."""

import pandas as pd
from pydantic import ValidationError as PydanticValidationError

from .contract import ExchangeRate


class ExchangeRateValidator:
    """Valida registros de divisas y detecta duplicados."""

    def validate_data(
        self, df: pd.DataFrame
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Separa registros válidos e inválidos."""

        valid_records = []
        invalid_records = []

        for index, row in enumerate(df.to_dict(orient="records"), start=2):
            try:
                record = ExchangeRate.model_validate(row)
                valid_records.append(record.model_dump(mode="json"))

            except PydanticValidationError as error:
                invalid_record = row.copy()
                invalid_record["error"] = str(error)
                invalid_record["row_number"] = index
                invalid_records.append(invalid_record)

        valid_df = pd.DataFrame(
            valid_records,
            columns=["date", "base", "quote", "rate"],
        )

        invalid_df = pd.DataFrame(invalid_records)

        return valid_df, invalid_df

    def remove_duplicates(
        self, df: pd.DataFrame
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Elimina duplicados por fecha y par de monedas."""

        columns = ["date", "base", "quote"]

        duplicates = df.duplicated(subset=columns, keep="first")

        clean_df = df.loc[~duplicates].copy()
        duplicate_df = df.loc[duplicates].copy()

        return clean_df, duplicate_df