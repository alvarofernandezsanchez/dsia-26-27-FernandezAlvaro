
import json
import logging

import pandas as pd
from openai import OpenAI

from .config import AppConfig


# Clase encargada de generar informes financieros mediante IA
class AIClient:

    def __init__(self, config: AppConfig):
        """Guarda la configuración del cliente de IA."""
        self.config = config
        self.logger = logging.getLogger("divisas_app")

    def generate_report(self, metrics: pd.DataFrame) -> str:
        """Genera un informe usando el modo mock o real."""

        if metrics.empty:
            raise ValueError("No hay métricas para generar el informe")

        if self.config.ai_mode == "mock":
            return self._mock_report(metrics)

        if self.config.ai_mode == "real":
            return self._real_report(metrics)

        raise ValueError("Modo de IA no válido")

    def _mock_report(self, metrics: pd.DataFrame) -> str:
        """Genera un informe de prueba sin consultar ninguna API."""

        self.logger.info("Generando informe en modo mock")

        lines = [
            "# Informe de divisas",
            "",
            "Modo: MOCK (sin IA real)",
            "",
            "## Resumen de cotizaciones",
            ""
        ]

        for _, row in metrics.iterrows():
            lines.append(
                f"- {row['base']}/{row['quote']}: "
                f"media {row['mean_rate']:.4f}, "
                f"variación {row['variation_pct']:+.2f}%"
            )

        return "\n".join(lines)

    def _real_report(self, metrics: pd.DataFrame) -> str:
        """Solicita a OpenAI un informe basado en las métricas."""

        self.logger.info("Generando informe mediante OpenAI")

        if not self.config.openai_api_key:
            raise ValueError("Falta OPENAI_API_KEY")

        # Convertimos las métricas a un formato que pueda leer la API
        data = metrics.to_dict(orient="records")
        metrics_json = json.dumps(data, ensure_ascii=False)

        # Creamos el cliente con la clave configurada
        client = OpenAI(
            api_key=self.config.openai_api_key,
            timeout=30.0,
            max_retries=2
        )

        # Enviamos las métricas al modelo de IA
        response = client.responses.create(
            model=self.config.openai_model,
            instructions=(
                "Eres un analista de datos financieros. "
                "Redacta en español un informe claro y breve "
                "sobre las cotizaciones de divisas proporcionadas. "
                "Utiliza únicamente las cifras recibidas. "
                "No inventes datos, causas económicas ni predicciones. "
                "No proporciones recomendaciones de inversión."
            ),
            input=(
                "Analiza estas métricas de tipos de cambio "
                "y genera un informe en formato Markdown:\n"
                f"{metrics_json}"
            )
        )

        if not response.output_text:
            raise RuntimeError("La API no devolvió un informe")

        return response.output_text
