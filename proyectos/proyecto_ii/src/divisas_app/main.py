
import logging
from pathlib import Path

from .ai_client import AIClient
from .config import load_config
from .inference import ExchangeRateAnalyzer
from .logging_config import setup_logging
from .preprocess import ExchangeRatePreprocessor


# Función principal que coordina el pipeline completo
def run_pipeline(
    input_path: str,
    output_dir: str,
    ai_mode: str | None = None
):
    """Carga, valida, limpia, analiza y exporta los datos."""

    # 1. Configuramos el sistema de logs
    setup_logging(output_dir)
    logger = logging.getLogger("divisas_app")

    logger.info("Iniciando pipeline de divisas")

    # 2. Creamos la carpeta de resultados si no existe
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    # 3. Cargamos el dataset original
    processor = ExchangeRatePreprocessor(input_path)
    df = processor.load_data()
    logger.info("Registros cargados: %s", len(df))

    # 4. Validamos cada registro con Pydantic
    validos, invalidos = processor.validate_data(df)
    logger.info("Registros válidos: %s", len(validos))
    logger.info("Registros inválidos: %s", len(invalidos))

    # 5. Separamos los registros duplicados
    limpios, duplicados = processor.remove_duplicates(validos)
    logger.info("Duplicados detectados: %s", len(duplicados))
    logger.info("Registros limpios: %s", len(limpios))

    # 6. Calculamos las estadísticas de las divisas
    analyzer = ExchangeRateAnalyzer(limpios)
    report = analyzer.generate_report()
    logger.info("Métricas calculadas correctamente")

    # 7. Guardamos los resultados en archivos CSV
    limpios.to_csv(output / "divisas_limpias.csv", index=False)
    invalidos.to_csv(output / "registros_invalidos.csv", index=False)
    duplicados.to_csv(output / "duplicados.csv", index=False)
    report.to_csv(output / "metricas_divisas.csv", index=False)

    logger.info("Archivos CSV guardados en: %s", output)

    # 8. Cargamos la configuración de la IA
    # Si recibimos ai_mode desde el CLI, tiene prioridad sobre .env
    config = load_config(ai_mode)

    # Creamos el cliente de inteligencia artificial
    ai_client = AIClient(config)

    # Generamos un informe a partir de las métricas
    logger.info("Generando informe de IA en modo %s", config.ai_mode)
    informe_ia = ai_client.generate_report(report)

    # Guardamos el informe en un archivo Markdown
    informe_path = output / "informe_ia.md"
    informe_path.write_text(informe_ia, encoding="utf-8")

    logger.info("Informe de IA guardado en: %s", informe_path)

    # 9. Mostramos un resumen del procesamiento
    print(f"Registros originales: {len(df)}")
    print(f"Registros válidos: {len(validos)}")
    print(f"Registros inválidos: {len(invalidos)}")
    print(f"Duplicados: {len(duplicados)}")
    print(f"Registros limpios: {len(limpios)}")
    print(f"\nResultados guardados en: {output}")

    logger.info("Pipeline finalizado correctamente")

    return report
