"""Orquestación del pipeline de calidad de datos de divisas."""

from pathlib import Path

from .loader import ExchangeRateLoader
from .validator import ExchangeRateValidator
from .metrics import ExchangeRateMetrics


def run_pipeline(input_path: str, output_dir: str):
    """Carga, valida, limpia, analiza y exporta los datos."""

    # 1. Creamos la carpeta de resultados
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    # 2. Cargamos el CSV
    loader = ExchangeRateLoader(input_path)
    df = loader.load_data()

    # 3. Validamos los registros
    validator = ExchangeRateValidator()
    validos, invalidos = validator.validate_data(df)

    # 4. Eliminamos duplicados
    limpios, duplicados = validator.remove_duplicates(validos)

    # 5. Calculamos las métricas
    metrics = ExchangeRateMetrics(limpios)
    report = metrics.generate_report()

    # 6. Exportamos los resultados
    limpios.to_csv(output / "divisas_limpias.csv", index=False)
    invalidos.to_csv(output / "registros_invalidos.csv", index=False)
    duplicados.to_csv(output / "duplicados.csv", index=False)
    report.to_csv(output / "metricas_divisas.csv", index=False)

    # 7. Mostramos un resumen
    print(f"Registros originales: {len(df)}")
    print(f"Registros válidos: {len(validos)}")
    print(f"Registros inválidos: {len(invalidos)}")
    print(f"Duplicados: {len(duplicados)}")
    print(f"Registros limpios: {len(limpios)}")

    print(f"\nResultados guardados en: {output}")

    return report