
import pytest

from ventas_app.loader import ErrorCargaVentas, VentasLoader


def test_loader_carga_csv_correctamente(tmp_path):
    # Arrange: creamos un CSV válido
    archivo = tmp_path / "ventas.csv"
    archivo.write_text(
        "fecha,region,producto,unidades,precio_unitario,cliente_id\n"
        "2026-01-05,Norte,Sensor A,12,19.5,C001\n"
        "2026-01-05,Sur,Sensor B,4,32.0,C002\n",
        encoding="utf-8",
    )

    # Act: cargamos el archivo
    filas = VentasLoader(archivo).cargar()

    # Assert: comprobamos los resultados
    assert len(filas) == 2
    assert filas[0]["region"] == "Norte"
    assert filas[0]["producto"] == "Sensor A"
    assert filas[0]["unidades"] == "12"


def test_loader_archivo_inexistente(tmp_path):
    archivo = tmp_path / "no_existe.csv"

    with pytest.raises(ErrorCargaVentas, match="No se encuentra"):
        VentasLoader(archivo).cargar()


def test_loader_csv_vacio(tmp_path):
    archivo = tmp_path / "vacio.csv"
    archivo.write_text("", encoding="utf-8")

    with pytest.raises(ErrorCargaVentas, match="vacío"):
        VentasLoader(archivo).cargar()
