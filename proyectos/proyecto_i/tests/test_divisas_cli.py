
import sys
from unittest.mock import patch

from divisas_app.cli import main


def test_cli_divisas_ejecuta_pipeline(tmp_path):
    entrada = tmp_path / "divisas.csv"
    salida = tmp_path / "resultados"

    entrada.write_text(
        "date,base,quote,rate\n"
        "2026-01-01,EUR,USD,1.10\n",
        encoding="utf-8",
    )

    with patch.object(
        sys,
        "argv",
        [
            "divisas_app",
            "--input",
            str(entrada),
            "--output",
            str(salida),
        ],
    ):
        with patch("divisas_app.cli.run_pipeline") as pipeline:
            main()

    pipeline.assert_called_once_with(
        str(entrada),
        str(salida),
    )
