"""Carga de datos de ventas desde archivos CSV."""

import csv
from pathlib import Path


class ErrorCargaVentas(Exception):
    """Error relacionado con la carga de datos de ventas."""


class VentasLoader:
    """Clase encargada de cargar las ventas desde un CSV."""

    def __init__(self, ruta: str | Path):
        self.ruta = Path(ruta)

    def cargar(self) -> list[dict[str, str]]:
        """Carga el CSV y devuelve sus filas como diccionarios."""

        if not self.ruta.is_file():
            raise ErrorCargaVentas(
                f"No se encuentra el archivo: {self.ruta}"
            )

        try:
            with self.ruta.open(
                mode="r", encoding="utf-8-sig", newline=""
            ) as archivo:
                lector = csv.DictReader(archivo)

                if lector.fieldnames is None:
                    raise ErrorCargaVentas("El archivo CSV está vacío.")

                return list(lector)

        except (OSError, UnicodeError, csv.Error) as error:
            raise ErrorCargaVentas(
                f"No se pudo cargar el archivo: {error}"
            ) from error