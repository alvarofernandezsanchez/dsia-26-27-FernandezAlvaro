
import logging
from pathlib import Path


# Configura los logs del programa
def setup_logging(output_dir: str = "resultados") -> None:
    """Muestra los logs en terminal y los guarda en un archivo."""

    # Creamos la carpeta de resultados si no existe
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    # Creamos el logger principal de nuestra aplicación
    logger = logging.getLogger("divisas_app")
    logger.setLevel(logging.INFO)

    # Evitamos añadir los mismos handlers varias veces
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    # Definimos el formato de los mensajes
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    # Mostramos los mensajes en la terminal
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Guardamos también los mensajes en un archivo
    file_handler = logging.FileHandler(
        output / "pipeline.log",
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # Activamos ambos destinos
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
