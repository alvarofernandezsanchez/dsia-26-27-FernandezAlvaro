"""Validación de los datos de ventas."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation


class ErrorValidacionVentas(Exception):
    """Error cuando una venta contiene datos incorrectos."""


@dataclass(frozen=True)
class Venta:
    """Representa una venta validada."""

    fecha: date
    region: str
    producto: str
    unidades: int
    precio_unitario: Decimal
    cliente_id: str


class VentasValidator:
    """Comprueba y convierte los datos de ventas."""

    COLUMNAS = {
        "fecha",
        "region",
        "producto",
        "unidades",
        "precio_unitario",
        "cliente_id",
    }

    def validar(self, filas: list[dict]) -> list[Venta]:
        """Valida todas las filas y devuelve objetos Venta."""

        ventas = []

        for numero, fila in enumerate(filas, start=2):
            ventas.append(self.validar_fila(fila, numero))

        return ventas

    def validar_fila(self, fila: dict, numero: int) -> Venta:
        """Valida una fila individual del CSV."""

        if not self.COLUMNAS.issubset(fila):
            raise ErrorValidacionVentas(
                f"Fila {numero}: faltan columnas obligatorias."
            )

        for columna in self.COLUMNAS:
            valor = fila[columna]

            if not isinstance(valor, str) or not valor.strip():
                raise ErrorValidacionVentas(
                    f"Fila {numero}: el campo '{columna}' está vacío."
                )

        try:
            fecha = date.fromisoformat(fila["fecha"].strip())
            unidades = int(fila["unidades"].strip())
            precio = Decimal(fila["precio_unitario"].strip())

        except (ValueError, InvalidOperation) as error:
            raise ErrorValidacionVentas(
                f"Fila {numero}: fecha, unidades o precio incorrectos."
            ) from error

        if unidades <= 0:
            raise ErrorValidacionVentas(
                f"Fila {numero}: las unidades deben ser positivas."
            )

        if not precio.is_finite() or precio < 0:
            raise ErrorValidacionVentas(
                f"Fila {numero}: el precio debe ser un número no negativo."
            )

        return Venta(
            fecha=fecha,
            region=fila["region"].strip(),
            producto=fila["producto"].strip(),
            unidades=unidades,
            precio_unitario=precio,
            cliente_id=fila["cliente_id"].strip(),
        )