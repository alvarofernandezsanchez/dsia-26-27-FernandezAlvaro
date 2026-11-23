
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
    ai_provider: str = "openai"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    nvidia_api_key: str = ""
    nvidia_model: str = ""
    log_level: str = "INFO"


# Función que obtiene la configuración del entorno
def load_config(ai_mode: str | None = None) -> AppConfig:
    """Lee las variables y permite seleccionar el modo de IA."""

    # El argumento del CLI tiene prioridad sobre el archivo .env
    config = AppConfig(
        ai_mode=(ai_mode or os.getenv("AI_MODE", "mock")).lower(),
        ai_provider=os.getenv("AI_PROVIDER", "openai").lower(),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        nvidia_api_key=os.getenv("NVIDIA_API_KEY", ""),
        nvidia_model=os.getenv("NVIDIA_MODEL", ""),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )

    if config.ai_mode not in ("mock", "real"):
        raise ValueError("AI_MODE debe ser 'mock' o 'real'")

    if config.ai_provider not in ("openai", "nvidia"):
        raise ValueError("AI_PROVIDER debe ser 'openai' o 'nvidia'")

    if config.ai_mode == "real":
        if config.ai_provider == "openai" and not config.openai_api_key:
            raise ValueError("Falta OPENAI_API_KEY")

        if config.ai_provider == "nvidia" and not config.nvidia_api_key:
            raise ValueError("Falta NVIDIA_API_KEY")

    return config
