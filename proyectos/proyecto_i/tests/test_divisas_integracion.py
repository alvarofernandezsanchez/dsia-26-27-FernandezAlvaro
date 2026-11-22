"""Test de integración del pipeline completo de divisas."""

import subprocess
import sys

import pandas as pd


def test_pipeline_divisas_completo(tmp_path):
    """Comprueba la CLI y los archivos generados."""

    entrada = tmp_path / "divisas.csv"
    salida = tmp_path / "resultados"

    entrada.write_text(
        "date,base,quote,rate\n"
        "2026-01-01,EUR,USD,1.10\n"
        "2026-01-02,EUR,USD,1.20\n"
        "2026-01-02,EUR,USD,1.20\n"
        "2026-01-03,EUR,USD,-1.00\n",
        encoding="utf-8",
    )

    resultado = subprocess.run(
        [
            sys.executable,
            "-m",
            "divisas_app.cli",
            "--input",
            str(entrada),
            "--output",
            str(salida),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert resultado.returncode == 0, resultado.stderr

    assert "Registros originales: 4" in resultado.stdout
    assert "Registros válidos: 3" in resultado.stdout
    assert "Registros inválidos: 1" in resultado.stdout
    assert "Duplicados: 1" in resultado.stdout
    assert "Registros limpios: 2" in resultado.stdout

    archivos = [
        "divisas_limpias.csv",
        "registros_invalidos.csv",
        "duplicados.csv",
        "metricas_divisas.csv",
    ]

    for nombre in archivos:
        assert (salida / nombre).is_file()

    limpios = pd.read_csv(salida / "divisas_limpias.csv")
    informe = pd.read_csv(salida / "metricas_divisas.csv")

    assert len(limpios) == 2
    assert informe.iloc[0]["mean_rate"] == 1.15
    assert informe.iloc[0]["num_records"] == 2