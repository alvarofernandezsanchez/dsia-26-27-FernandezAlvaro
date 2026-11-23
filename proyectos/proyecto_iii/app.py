
import logging
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from divisas_app.ai_client import AIClient
from divisas_app.config import load_config
from divisas_app.inference import ExchangeRateAnalyzer
from divisas_app.logging_config import setup_logging
from divisas_app.preprocess import ExchangeRatePreprocessor
from divisas_app.sklearn_inference import predict_next_rates

# Configuración de Streamlit
st.set_page_config(
    page_title="Divisas AI",
    page_icon="💱",
    layout="wide",
)

# Configuración de los logs
setup_logging(str(Path(__file__).parent / "resultados"))
logger = logging.getLogger("divisas_app")


st.title("💱 Divisas AI")
st.write("Plataforma de análisis y predicción de tipos de cambio")

st.sidebar.header("Navegación")

pagina = st.sidebar.radio(
    "Selecciona una sección",
    ["Inicio", "Análisis de divisas", "Predicciones", "Informe IA"],
)


# INICIO
if pagina == "Inicio":
    st.subheader("Bienvenido a Divisas AI")
    st.write("Consulta cotizaciones, analiza datos y genera predicciones.")


# ANÁLISIS HISTÓRICO
elif pagina == "Análisis de divisas":
    st.subheader("Análisis histórico de divisas")

    ruta = Path(__file__).parent / "datos" / "divisas.csv"

    df = pd.read_csv(ruta)
    df["date"] = pd.to_datetime(df["date"])
    df["rate"] = pd.to_numeric(df["rate"], errors="coerce")

    pares = sorted(
        (df["base"] + "/" + df["quote"]).unique()
    )

    par = st.selectbox("Selecciona un par de divisas", pares)

    base, quote = par.split("/")

    filtrado = df[
        (df["base"] == base) &
        (df["quote"] == quote)
    ].copy()

    filtrado = filtrado.dropna(subset=["date", "rate"])
    filtrado = filtrado.sort_values("date")

    st.metric("Última cotización", f"{filtrado['rate'].iloc[-1]:.4f}")

    st.subheader(f"Evolución histórica de {par}")
    st.line_chart(filtrado.set_index("date")["rate"])

    st.subheader("Datos históricos")
    st.dataframe(filtrado, use_container_width=True)


# PREDICCIONES
elif pagina == "Predicciones":
    st.subheader("Predicciones con Machine Learning")

    ruta_csv = Path(__file__).parent / "datos" / "divisas.csv"
    ruta_modelo = Path(__file__).parent / "modelos" / "divisas_model.joblib"

    if st.button("Generar predicciones"):
        st.session_state.pop("predicciones", None)

        try:
            with st.spinner("Actualizando cotizaciones y generando predicciones..."):

                logger.info("Consultando cotizaciones en Frankfurter")

                processor = ExchangeRatePreprocessor(str(ruta_csv))
                df = processor.update_from_api()

                logger.info("Cotizaciones disponibles: %s", len(df))

                st.session_state["predicciones"] = predict_next_rates(
                    df,
                    model_path=str(ruta_modelo),
                )

                logger.info(
                    "Predicciones generadas correctamente: %s",
                    len(st.session_state["predicciones"]),
                )

                st.success("Cotizaciones consultadas y predicciones generadas.")

        except Exception as error:
            logger.exception("Error al generar predicciones")
            st.error(f"No se pudo generar la predicción: {error}")

    if "predicciones" in st.session_state:
        predicciones = st.session_state["predicciones"]

        if predicciones.empty:
            st.warning("No hay predicciones disponibles.")

        else:
            pares = (
                predicciones["base"] + "/" + predicciones["quote"]
            ).tolist()

            par = st.selectbox("Selecciona un par de divisas", pares)

            base, quote = par.split("/")

            resultado = predicciones[
                (predicciones["base"] == base)
                & (predicciones["quote"] == quote)
            ].iloc[0]

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Última cotización",
                    f"{resultado['last_rate']:.4f}",
                )

            with col2:
                st.metric(
                    "Siguiente cotización estimada",
                    f"{resultado['predicted_next_rate']:.4f}",
                )

            st.caption(
                f"Último dato disponible: {resultado['date']}. "
                "Predicción de la siguiente cotización disponible."
            )


# INFORMES DE IA
elif pagina == "Informe IA":
    st.subheader("Informe de divisas con IA")

    ruta_csv = Path(__file__).parent / "datos" / "divisas.csv"

    df = pd.read_csv(ruta_csv)
    df["date"] = pd.to_datetime(df["date"])

    modo = st.selectbox(
        "Modo de generación",
        ["mock", "real"],
    )

    proveedor = None

    if modo == "real":
        proveedor = st.selectbox(
            "Proveedor de IA",
            ["nvidia", "openai"],
        )

    if st.button("Generar informe"):
        st.session_state.pop("informe_ia", None)

        try:
            with st.spinner("Generando informe..."):

                logger.info("Generando informe IA en modo %s", modo)

                config = load_config(ai_mode="mock")
                config.ai_mode = modo

                if proveedor:
                    config.ai_provider = proveedor
                    logger.info("Proveedor de IA: %s", proveedor)

                analyzer = ExchangeRateAnalyzer(df)
                metricas = analyzer.generate_report()

                logger.info("Métricas calculadas: %s", len(metricas))

                cliente = AIClient(config)
                informe = cliente.generate_report(metricas)

                st.session_state["informe_ia"] = informe

                logger.info("Informe IA generado correctamente")

        except Exception as error:
            logger.exception("Error al generar informe IA")
            st.error(f"No se pudo generar el informe: {error}")

    if "informe_ia" in st.session_state:
        st.markdown(st.session_state["informe_ia"])

        st.download_button(
            label="Descargar informe",
            data=st.session_state["informe_ia"],
            file_name="informe_ia.md",
            mime="text/markdown",
        )