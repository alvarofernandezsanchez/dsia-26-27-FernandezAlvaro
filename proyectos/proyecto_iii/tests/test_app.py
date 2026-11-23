from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def test_inicio():
    app = AppTest.from_file(str(APP_PATH)).run()

    assert not app.exception
    assert app.title[0].value == "💱 Divisas AI"


def test_analisis_historico():
    app = AppTest.from_file(str(APP_PATH)).run()

    app.sidebar.radio[0].set_value("Análisis de divisas").run()

    assert not app.exception
    assert len(app.metric) == 1
    assert len(app.dataframe) == 1


def test_pagina_predicciones():
    app = AppTest.from_file(str(APP_PATH)).run()

    app.sidebar.radio[0].set_value("Predicciones").run()

    assert not app.exception
    assert app.button[0].label == "Generar predicciones"


def test_informe_mock():
    app = AppTest.from_file(str(APP_PATH)).run()

    app.sidebar.radio[0].set_value("Informe IA").run()
    app.selectbox[0].set_value("mock").run()
    app.button[0].click().run()

    assert not app.exception
    assert not app.error
    assert "informe_ia" in app.session_state
    assert "MOCK" in app.session_state["informe_ia"]