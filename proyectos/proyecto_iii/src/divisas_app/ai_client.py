
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

        self.logger.info(
            "Generando informe mediante %s",
            self.config.ai_provider,
        )

        if self.config.ai_provider == "nvidia":
            api_key = self.config.nvidia_api_key
            model = self.config.nvidia_model
            base_url = "https://integrate.api.nvidia.com/v1"

        elif self.config.ai_provider == "openai":
            api_key = self.config.openai_api_key
            model = self.config.openai_model
            base_url = None

        else:
            raise ValueError("Proveedor de IA no válido")

        if not api_key:
            raise ValueError(
                f"Falta la API key del proveedor {self.config.ai_provider}"
            )

        # Convertimos las métricas a un formato que pueda leer la API
        data = metrics.to_dict(orient="records")
        metrics_json = json.dumps(data, ensure_ascii=False)

        # Creamos el cliente con la clave configurada
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=30.0,
            max_retries=2,
        )

        # Enviamos las métricas al modelo de IA
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un analista de datos financieros. "
                        "Redacta en español un informe claro y breve "
                        "sobre las cotizaciones de divisas proporcionadas. "
                        "Utiliza únicamente las cifras recibidas. "
                        "No inventes datos, causas económicas ni predicciones. "
                        "No proporciones recomendaciones de inversión."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Analiza estas métricas de tipos de cambio "
                        "y genera un informe en formato Markdown:\n"
                        f"{metrics_json}"
                    ),
                },
            ],
        )

        if not response.choices:
            raise RuntimeError("La API no devolvió ninguna respuesta")

        report = response.choices[0].message.content

        if not report:
            raise RuntimeError("La API no devolvió un informe")

        return report
