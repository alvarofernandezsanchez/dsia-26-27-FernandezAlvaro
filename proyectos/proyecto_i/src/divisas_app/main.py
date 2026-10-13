
from pathlib import Path

from .preprocess import ExchangeRatePreprocessor
from .inference import ExchangeRateAnalyzer


# Función principal que coordina el pipeline completo
def run_pipeline(input_path: str, output_dir: str):
    """Carga, valida, limpia, analiza y exporta los datos."""

    #Creamos la carpeta de resultados si no existe
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    #1.Cargamos el dataset original
    processor = ExchangeRatePreprocessor(input_path)
    df = processor.load_data()

    #2.Validamos cada registro con Pydantic
    validos, invalidos = processor.validate_data(df)

    #3.Separamos los registros duplicados
    limpios, duplicados = processor.remove_duplicates(validos)

    #4.Calculamos las estadísticas de las divisas
    analyzer = ExchangeRateAnalyzer(limpios)
    report = analyzer.generate_report()

    #5.Guardamos los resultados en archivos CSV
    limpios.to_csv(output / "divisas_limpias.csv", index=False)
    invalidos.to_csv(output / "registros_invalidos.csv", index=False)
    duplicados.to_csv(output / "duplicados.csv", index=False)
    report.to_csv(output / "metricas_divisas.csv", index=False)

    #6.Mostramos un resumen del procesamiento
    print(f"Registros originales: {len(df)}")
    print(f"Registros válidos: {len(validos)}")
    print(f"Registros inválidos: {len(invalidos)}")
    print(f"Duplicados: {len(duplicados)}")
    print(f"Registros limpios: {len(limpios)}")

    print(f"\nResultados guardados en: {output}")

    return report
