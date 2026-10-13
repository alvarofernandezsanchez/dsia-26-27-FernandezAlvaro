
import argparse

from .main import run_pipeline
from .preprocess import ExchangeRatePreprocessor
from .contract import DataLoadError, ValidationError


# Función principal que recibe los argumentos de la terminal
def main():
    """Permite actualizar y procesar el dataset de divisas."""

    parser = argparse.ArgumentParser(
        description="Pipeline de calidad de datos de divisas"
    )

    # Ruta del CSV que queremos procesar
    parser.add_argument(
        "--input",
        default="datos/divisas.csv",
        help="Ruta del CSV de entrada"
    )

    # Carpeta donde guardaremos los resultados
    parser.add_argument(
        "--output",
        default="resultados",
        help="Carpeta de salida"
    )

    # Opción para descargar nuevas cotizaciones desde Frankfurter
    parser.add_argument(
        "--update",
        action="store_true",
        help="Actualiza el dataset desde la API"
    )

    args = parser.parse_args()

    try:
        if args.update:
            # Actualizamos el CSV antes de procesarlo
            print("Consultando Frankfurter...")
            processor = ExchangeRatePreprocessor(args.input)
            actualizado = processor.update_from_api()
            print(f"Registros disponibles: {len(actualizado)}")

        # Ejecutamos el pipeline de calidad de datos
        run_pipeline(args.input, args.output)

    except (DataLoadError, ValidationError, OSError) as error:
        # Mostramos un mensaje comprensible si algo falla
        parser.exit(1, f"Error: {error}\n")


# Permite ejecutar el archivo como módulo de Python
if __name__ == "__main__":
    main()
