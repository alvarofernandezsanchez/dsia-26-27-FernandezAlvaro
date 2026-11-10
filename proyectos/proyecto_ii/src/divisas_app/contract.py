from datetime import date
from pydantic import BaseModel, Field, field_validator


class DataLoadError(Exception):
    """Error al cargar los datos."""

class ValidationError(Exception):
    """Error cuando los datos no cumplen las reglas."""

class ExchangeRate(BaseModel):
    """Representa un registro válido de tipo de cambio."""

    date: date
    base: str
    quote: str
    rate: float = Field(gt=0)#asi fuerzo a que el tipo de cambio sea positivo

    @field_validator("base", "quote")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        """Comprueba el formato del código de moneda."""

        if len(value) != 3 or not value.isalpha():
            raise ValueError(
                "La moneda debe tener tres letras"
            )

        if value != value.upper():
            raise ValueError(
                "El código de moneda debe estar en mayúsculas"
            )

        return value

    @field_validator("quote")
    @classmethod
    def validate_different_currencies(
        cls, value: str, info
    ) -> str:
        """Comprueba que las monedas sean diferentes."""

        if value == info.data.get("base"):
            raise ValueError(
                "La moneda de origen y destino deben ser distintas"
            )

        return value