
import os
from dataclasses import dataclass
from dotenv import load_dotenv


# Cargamos las variables del archivo .env
load_dotenv()


# Clase que almacena la configuración del programa
@dataclass
class AppConfig:
    """Guarda los parámetros necesarios para ejecutar el pipeline."""

    ai_mode: str = "mock"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    log_level: str = "INFO"


# Función que obtiene la configuración del entorno
def load_config(ai_mode: str | None = None) -> AppConfig:
    """Lee las variables y permite seleccionar el modo de IA."""

    # El argumento del CLI tiene prioridad sobre el archivo .env
    config = AppConfig(
        ai_mode=(ai_mode or os.getenv("AI_MODE", "mock")).lower(),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper()
    )

    # Comprobamos que el modo seleccionado sea válido
    if config.ai_mode not in ("mock", "real"):
        raise ValueError("AI_MODE debe ser 'mock' o 'real'")

    # Para utilizar IA real necesitamos una clave de API
    if config.ai_mode == "real" and not config.openai_api_key:
        raise ValueError("Falta OPENAI_API_KEY para utilizar el modo real")

    return config
