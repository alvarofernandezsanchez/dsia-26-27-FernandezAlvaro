"""Interfaz de línea de comandos del pipeline de ventas."""

import argparse
import sys
from pathlib import Path

from .loader import ErrorCargaVentas, VentasLoader
from .metrics import VentasMetrics
from .validator import ErrorValidacionVentas, VentasValidator


def main() -> int:
    """Ejecuta la carga, validación y análisis de ventas."""

    parser = argparse.ArgumentParser(
        description="Pipeline de calidad de datos de ventas."
    )

    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Ruta del archivo CSV de ventas.",
    )

    args = parser.parse_args()

    try:
        # 1. Cargar los datos
        filas = VentasLoader(args.input).cargar()

        # 2. Validar los datos
        ventas = VentasValidator().validar(filas)

        # 3. Calcular las métricas
        metricas = VentasMetrics(ventas)

    except (ErrorCargaVentas, ErrorValidacionVentas) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("\n=== INFORME DE VENTAS ===")
    print(f"Ventas procesadas: {len(ventas)}")
    print(f"Unidades vendidas: {metricas.unidades_totales()}")
    print(f"Importe total: {metricas.importe_total():.2f} €")

    print("\n--- Importe por región ---")
    for region, importe in metricas.importe_por_region().items():
        print(f"{region}: {importe:.2f} €")

    print("\n--- Importe por producto ---")
    for producto, importe in metricas.importe_por_producto().items():
        print(f"{producto}: {importe:.2f} €")

    return 0


if __name__ == "__main__":
    sys.exit(main())