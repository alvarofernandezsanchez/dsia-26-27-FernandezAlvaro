"""Pruebas de integración del pipeline completo de ventas."""

import subprocess
import sys


def test_pipeline_ventas_completo(tmp_path):
    """Comprueba la ejecución completa de la CLI con datos válidos."""

    archivo = tmp_path / "ventas.csv"

    archivo.write_text(
        "fecha,region,producto,unidades,precio_unitario,cliente_id\n"
        "2026-01-05,Norte,Sensor A,2,10.0,C001\n"
        "2026-01-06,Sur,Sensor B,3,20.0,C002\n",
        encoding="utf-8",
    )

    resultado = subprocess.run(
        [
            sys.executable,
            "-m",
            "ventas_app.cli",
            "--input",
            str(archivo),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert resultado.returncode == 0
    assert "Ventas procesadas: 2" in resultado.stdout
    assert "Unidades vendidas: 5" in resultado.stdout
    assert "Importe total: 80.00" in resultado.stdout
    assert "Norte: 20.00" in resultado.stdout
    assert "Sur: 60.00" in resultado.stdout


def test_pipeline_ventas_invalidas(tmp_path):
    """Comprueba que la CLI rechaza un CSV con datos incorrectos."""

    archivo = tmp_path / "ventas_invalidas.csv"

    archivo.write_text(
        "fecha,region,producto,unidades,precio_unitario,cliente_id\n"
        "2026-01-05,Norte,Sensor A,,10.0,C001\n",
        encoding="utf-8",
    )

    resultado = subprocess.run(
        [
            sys.executable,
            "-m",
            "ventas_app.cli",
            "--input",
            str(archivo),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert resultado.returncode == 1
    assert "ERROR:" in resultado.stderr
    assert "unidades" in resultado.stderr