
import pandas as pd

from divisas_app.main import run_pipeline


# Comprobamos el funcionamiento del pipeline completo
def test_pipeline_completo(tmp_path, monkeypatch):
    """Prueba el pipeline desde el CSV hasta el informe de IA."""

    # 1. Configuramos el modo mock para no utilizar una API real
    monkeypatch.setenv("AI_MODE", "mock")

    # 2. Creamos un CSV temporal con datos de ejemplo
    input_path = tmp_path / "divisas_prueba.csv"

    datos = pd.DataFrame([
        {"date": "2026-01-01", "base": "EUR", "quote": "USD", "rate": 1.10},
        {"date": "2026-01-02", "base": "EUR", "quote": "USD", "rate": 1.15},
        {"date": "2026-01-03", "base": "EUR", "quote": "USD", "rate": 1.20},
    ])

    datos.to_csv(input_path, index=False)

    # 3. Creamos una carpeta temporal para los resultados
    output_dir = tmp_path / "resultados"

    # 4. Ejecutamos el pipeline completo
    run_pipeline(str(input_path), str(output_dir))

    # 5. Comprobamos que se han generado los archivos
    assert (output_dir / "divisas_limpias.csv").exists()
    assert (output_dir / "registros_invalidos.csv").exists()
    assert (output_dir / "duplicados.csv").exists()
    assert (output_dir / "metricas_divisas.csv").exists()
    assert (output_dir / "pipeline.log").exists()
    assert (output_dir / "informe_ia.md").exists()

    # 6. Comprobamos que las métricas son correctas
    metricas = pd.read_csv(output_dir / "metricas_divisas.csv")

    assert len(metricas) == 1
    assert metricas.iloc[0]["num_records"] == 3
    assert round(metricas.iloc[0]["mean_rate"], 2) == 1.15

    # 7. Comprobamos el contenido del informe
    informe = (output_dir / "informe_ia.md").read_text(
        encoding="utf-8"
    )

    assert "EUR/USD" in informe
    assert "MOCK" in informe


def test_pipeline_completo_alternativo(tmp_path, monkeypatch):
    from divisas_app.main import run_pipeline

    # Creamos un CSV temporal para la prueba
    input_path = tmp_path / "divisas.csv"
    output_dir = tmp_path / "resultados"

    input_path.write_text(
        "date,base,quote,rate\n"
        "2026-01-01,EUR,USD,1.10\n"
        "2026-01-02,EUR,USD,1.20\n",
        encoding="utf-8"
    )

    # Evitamos depender de una API real o de la configuración local
    monkeypatch.setenv("AI_MODE", "mock")

    # Ejecutamos el pipeline completo
    report = run_pipeline(
        input_path=str(input_path),
        output_dir=str(output_dir),
        ai_mode="mock"
    )

    # Comprobamos que se generan los archivos
    assert (output_dir / "divisas_limpias.csv").exists()
    assert (output_dir / "registros_invalidos.csv").exists()
    assert (output_dir / "duplicados.csv").exists()
    assert (output_dir / "metricas_divisas.csv").exists()
    assert (output_dir / "informe_ia.md").exists()

    # Comprobamos que el informe contiene información
    assert not report.empty

    informe = (output_dir / "informe_ia.md").read_text(encoding="utf-8")
    assert "MOCK" in informe
