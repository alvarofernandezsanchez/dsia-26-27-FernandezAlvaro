
import sys
from unittest.mock import patch

from ventas_app.cli import main


def test_cli_ventas_correcta(tmp_path, capsys):
    # Creamos un CSV temporal con el formato correcto
    archivo = tmp_path / "ventas.csv"

    archivo.write_text(
        "fecha,region,producto,unidades,precio_unitario,cliente_id\n"
        "2026-01-05,Norte,Sensor A,12,19.5,C001\n"
        "2026-01-05,Sur,Sensor B,4,32.0,C002\n",
        encoding="utf-8",
    )

    # Simulamos los argumentos de la terminal
    with patch.object(
        sys, "argv", ["ventas_app", "--input", str(archivo)]
    ):
        resultado = main()

    salida = capsys.readouterr()

    # Comprobamos que el pipeline funciona
    assert resultado == 0
    assert "INFORME DE VENTAS" in salida.out
    assert "Ventas procesadas: 2" in salida.out
    assert "Unidades vendidas: 16" in salida.out
    assert "Importe total: 362.00" in salida.out
