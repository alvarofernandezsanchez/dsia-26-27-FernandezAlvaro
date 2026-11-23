import plotly.express as px
import plotly.graph_objects as go
import logging
import sys
from pathlib import Path
import time

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

css_path = Path(__file__).parent / "assets" / "styles.css"

st.markdown(
    f"<style>{css_path.read_text(encoding='utf-8')}</style>",
    unsafe_allow_html=True,
)

# Configuración de los logs
setup_logging(str(Path(__file__).parent / "resultados"))
logger = logging.getLogger("divisas_app")


st.markdown(
    """
    <div class="brand-title">
        DIVISAS<span class="brand-accent">.AI</span>
    </div>
    <div class="brand-subtitle">
        Intelligent FX Analytics
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

st.sidebar.header("Navegación")

pagina = st.sidebar.radio(
    "Selecciona una sección",
    ["Inicio", "Análisis de divisas", "Predicciones", "Informe IA"],
)


# INICIO

if pagina == "Inicio":

    st.header("Market Overview")
    st.caption("Inteligencia financiera y análisis del mercado de divisas")

    ruta_csv = Path(__file__).parent / "datos" / "divisas.csv"

    # Actualización de cotizaciones
    if st.button("Actualizar mercado", type="primary"):
        try:
            with st.spinner("Consultando Frankfurter..."):
                processor = ExchangeRatePreprocessor(str(ruta_csv))
                processor.update_from_api()

                logger.info("Mercado actualizado correctamente")
                st.success("Cotizaciones actualizadas correctamente")

        except Exception as error:
            logger.exception("Error al actualizar el mercado")
            st.error(f"No se pudo actualizar el mercado: {error}")

    # Cargamos los datos reales
    df = pd.read_csv(ruta_csv)
    df["date"] = pd.to_datetime(df["date"])
    df["rate"] = pd.to_numeric(df["rate"], errors="coerce")

    df = df.dropna(subset=["date", "rate"])
    df = df.sort_values("date")

    df["pair"] = df["base"] + "/" + df["quote"]

    # Indicadores generales
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Pares monitorizados",
        df["pair"].nunique(),
    )

    col2.metric(
        "Registros históricos",
        f"{len(df):,}",
    )

    col3.metric(
        "Última cotización",
        df["date"].max().strftime("%d/%m/%Y"),
    )

    col4.metric(
        "Motor predictivo",
        "Random Forest",
    )

    st.divider()

    # Calculamos las últimas cotizaciones y variaciones
    resumen = []

    for par, grupo in df.groupby("pair"):

        grupo = grupo.sort_values("date")

        ultima = grupo["rate"].iloc[-1]

        variacion = 0.0

        if len(grupo) >= 2:
            anterior = grupo["rate"].iloc[-2]
            variacion = ((ultima - anterior) / anterior) * 100

        resumen.append({
            "Par": par,
            "Cotización": ultima,
            "Variación (%)": variacion,
            "Fecha": grupo["date"].iloc[-1],
        })

    mercado = pd.DataFrame(resumen)

    # Principales divisas
    st.subheader("Principales mercados")

    principales = ["EUR/USD", "EUR/GBP", "EUR/JPY", "EUR/CHF"]

    columnas = st.columns(4)

    for columna, par in zip(columnas, principales):

        fila = mercado[mercado["Par"] == par]

        if not fila.empty:

            cotizacion = fila["Cotización"].iloc[0]
            variacion = fila["Variación (%)"].iloc[0]

            columna.metric(
                par,
                f"{cotizacion:.4f}",
                delta=f"{variacion:+.2f}%",
            )

        else:
            columna.metric(par, "N/D")

    st.divider()

    # Gráfico interactivo
    st.subheader("Market Performance")

    filtro1, filtro2 = st.columns(2)

    pares = sorted(df["pair"].unique())

    with filtro1:
        par = st.selectbox(
            "Par de divisas",
            pares,
            index=pares.index("EUR/USD") if "EUR/USD" in pares else 0,
        )

    with filtro2:
        periodo = st.selectbox(
            "Periodo",
            ["1 mes", "3 meses", "6 meses", "1 año", "Todo"],
            index=1,
        )

    filtrado = df[df["pair"] == par].copy()

    periodos = {
        "1 mes": 30,
        "3 meses": 90,
        "6 meses": 180,
        "1 año": 365,
    }

    if periodo != "Todo":

        fecha_limite = (
            filtrado["date"].max()
            - pd.Timedelta(days=periodos[periodo])
        )

        filtrado = filtrado[
            filtrado["date"] >= fecha_limite
        ]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=filtrado["date"],
            y=filtrado["rate"],
            mode="lines",
            name=par,
            line=dict(
                color="#36D9B3",
                width=2.5,
            ),
            fill="tozeroy",
            fillcolor="rgba(54, 217, 179, 0.08)",
            hovertemplate=(
                "%{x|%d/%m/%Y}<br>"
                "Cotización: %{y:.4f}<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#131E30",
        plot_bgcolor="#131E30",
        height=420,
        margin=dict(l=20, r=20, t=30, b=20),
        hovermode="x unified",
        font=dict(color="#E5EAF4"),
        xaxis=dict(
            showgrid=False,
        ),
        yaxis=dict(
            gridcolor="#263247",
            title="Tipo de cambio",
            rangemode="normal",
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    # Tabla del mercado
    st.subheader("Market Watch")

    st.dataframe(
        mercado.style.format({
            "Cotización": "{:.4f}",
            "Variación (%)": "{:+.2f}%",
            "Fecha": "{:%d/%m/%Y}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Fuente: Frankfurter API. "
        "Cotizaciones de referencia diarias, no intradía."
    )



# ANÁLISIS HISTÓRICO

elif pagina == "Análisis de divisas":

    st.header("Market Analytics")
    st.caption("Análisis avanzado y comparación de mercados")

    ruta_csv = Path(__file__).parent / "datos" / "divisas.csv"

    df = pd.read_csv(ruta_csv)
    df["date"] = pd.to_datetime(df["date"])
    df["pair"] = df["base"] + "/" + df["quote"]
    df = df.sort_values("date")

    pares = sorted(df["pair"].unique())

    col1, col2 = st.columns(2)

    with col1:
        seleccion = st.multiselect(
            "Seleccionar divisas",
            pares,
            default=pares[:2],
        )

    with col2:
        periodo = st.selectbox(
            "Horizonte temporal",
            ["1 mes", "3 meses", "6 meses", "1 año", "Todo"],
            index=3,
        )

    periodos = {
        "1 mes": 30,
        "3 meses": 90,
        "6 meses": 180,
        "1 año": 365,
    }

    if not seleccion:
        st.warning("Selecciona al menos una divisa.")
        st.stop()

    filtrado = df[df["pair"].isin(seleccion)].copy()

    if periodo != "Todo":
        fecha_limite = (
            df["date"].max()
            - pd.Timedelta(days=periodos[periodo])
        )

        filtrado = filtrado[
            filtrado["date"] >= fecha_limite
        ].copy()

    if filtrado.empty:
        st.warning("No hay datos para el periodo seleccionado.")
        st.stop()

    # Rentabilidad acumulada
    filtrado["rentabilidad"] = (
        filtrado.groupby("pair")["rate"]
        .transform(lambda x: (x / x.iloc[0] - 1) * 100)
    )

    # Variaciones entre cotizaciones
    filtrado["variacion_diaria"] = (
        filtrado.groupby("pair")["rate"].pct_change() * 100
    )

    st.divider()

    # Indicadores financieros
    st.subheader("Market Indicators")

    par_principal = st.selectbox(
        "Divisa para indicadores",
        seleccion,
    )

    datos_par = filtrado[
        filtrado["pair"] == par_principal
    ]

    if datos_par.empty:
        st.warning("No hay datos para esta divisa.")
        st.stop()

    ultima = datos_par["rate"].iloc[-1]
    rentabilidad = datos_par["rentabilidad"].iloc[-1]
    volatilidad = datos_par["variacion_diaria"].std()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Última cotización",
        f"{ultima:.4f}",
        delta=f"{rentabilidad:+.2f}%",
    )

    c2.metric(
        "Máximo del periodo",
        f"{datos_par['rate'].max():.4f}",
    )

    c3.metric(
        "Mínimo del periodo",
        f"{datos_par['rate'].min():.4f}",
    )

    c4.metric(
        "Volatilidad diaria",
        f"{volatilidad:.2f}%" if pd.notna(volatilidad) else "N/D",
    )

    st.divider()

    # Comparación de rentabilidad
    st.subheader("Comparative Performance")

    fig = px.line(
        filtrado,
        x="date",
        y="rentabilidad",
        color="pair",
        labels={
            "date": "Fecha",
            "rentabilidad": "Rentabilidad acumulada (%)",
            "pair": "Divisa",
        },
        color_discrete_sequence=[
            "#36D9B3",
            "#A78BFA",
            "#60A5FA",
            "#FBBF24",
            "#F87171",
            "#F472B6",
        ],
    )

    fig.update_traces(line=dict(width=2.5))

    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="#64748B",
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#131E30",
        plot_bgcolor="#131E30",
        height=450,
        hovermode="x unified",
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h"),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="#263247"),
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Las divisas se normalizan respecto a su primera "
        "cotización del periodo para facilitar su comparación."
    )

    # Distribución de variaciones
    st.subheader("Market Volatility")

    fig_vol = px.histogram(
        filtrado.dropna(subset=["variacion_diaria"]),
        x="variacion_diaria",
        color="pair",
        nbins=50,
        barmode="overlay",
        opacity=0.65,
        labels={
            "variacion_diaria": "Variación diaria (%)",
            "pair": "Divisa",
        },
        color_discrete_sequence=[
            "#36D9B3",
            "#A78BFA",
            "#60A5FA",
            "#FBBF24",
        ],
    )

    fig_vol.update_layout(
        template="plotly_dark",
        paper_bgcolor="#131E30",
        plot_bgcolor="#131E30",
        height=350,
        bargap=0.05,
        yaxis_title="Frecuencia",
        margin=dict(l=20, r=20, t=30, b=20),
    )

    st.plotly_chart(fig_vol, use_container_width=True)

    # Datos históricos
    with st.expander("Consultar datos históricos"):

        st.dataframe(
            filtrado,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Descargar datos CSV",
            data=filtrado.to_csv(index=False),
            file_name="market_analytics.csv",
            mime="text/csv",
        )



# PREDICCIONES

elif pagina == "Predicciones":

    st.header("ML Forecast")
    st.caption("Machine Learning · Predictive Intelligence")

    ruta_csv = Path(__file__).parent / "datos" / "divisas.csv"
    ruta_modelo = Path(__file__).parent / "modelos" / "divisas_model.joblib"
    ruta_test = Path(__file__).parent / "modelos" / "predicciones_test.csv"
    ruta_metricas = Path(__file__).parent / "modelos" / "metricas_modelo.csv"

    # Información general del modelo
    metricas = pd.read_csv(ruta_metricas).iloc[0]

    c1, c2, c3 = st.columns(3)

    c1.metric("Modelos entrenados", int(metricas["num_models"]))
    c2.metric("Registros de entrenamiento", f"{int(metricas['train_rows']):,}")
    c3.metric("Registros de evaluación", f"{int(metricas['test_rows']):,}")

    st.divider()

    # Generación de predicciones
    st.subheader("Prediction Engine")

    if st.button("Actualizar mercado y generar predicciones", type="primary"):

        try:
            with st.spinner("Actualizando datos y ejecutando Random Forest..."):

                processor = ExchangeRatePreprocessor(str(ruta_csv))
                processor.update_from_api()

                df = pd.read_csv(ruta_csv)

                predicciones = predict_next_rates(
                    df,
                    model_path=str(ruta_modelo),
                )

                st.session_state["ml_forecasts"] = predicciones

                logger.info(
                    "Predicciones generadas para %s pares",
                    len(predicciones),
                )

                st.success("Predicciones generadas correctamente.")

        except Exception:
            logger.exception("Error generando predicciones")
            st.error("No se pudieron generar las predicciones.")

    if "ml_forecasts" in st.session_state:

        predicciones = st.session_state["ml_forecasts"].copy()

        predicciones["pair"] = (
            predicciones["base"] + "/" + predicciones["quote"]
        )

        if not predicciones.empty:

            par = st.selectbox(
                "Seleccionar divisa",
                sorted(predicciones["pair"].unique()),
            )

            fila = predicciones[
                predicciones["pair"] == par
            ].iloc[0]

            ultima = float(fila["last_rate"])
            prediccion = float(fila["predicted_next_rate"])
            variacion = ((prediccion / ultima) - 1) * 100

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Última cotización",
                f"{ultima:.4f}",
            )

            c2.metric(
                "Predicción Random Forest",
                f"{prediccion:.4f}",
            )

            c3.metric(
                "Variación estimada",
                f"{variacion:+.3f}%",
            )

            st.caption(
                f"Última cotización disponible: {fila['date']}"
            )

            # Histórico de la divisa
            historico = pd.read_csv(ruta_csv)
            historico["date"] = pd.to_datetime(historico["date"])
            historico["pair"] = (
                historico["base"] + "/" + historico["quote"]
            )

            fecha_actual = pd.Timestamp(fila["date"])

            historico = historico[
                (historico["pair"] == par)
                & (historico["date"] <= fecha_actual)
            ].sort_values("date").tail(60)

            fecha_siguiente = fecha_actual + pd.offsets.BDay(1)

            fig = go.Figure()

            # Cotizaciones históricas
            fig.add_trace(
                go.Scatter(
                    x=historico["date"],
                    y=historico["rate"],
                    mode="lines",
                    name="Cotización real",
                    line=dict(color="#36D9B3", width=2.5),
                )
            )

            # Predicción Random Forest
            fig.add_trace(
                go.Scatter(
                    x=[fecha_actual, fecha_siguiente],
                    y=[ultima, prediccion],
                    mode="lines+markers",
                    name="Random Forest",
                    line=dict(
                        color="#A78BFA",
                        width=3,
                        dash="dash",
                    ),
                    marker=dict(size=9),
                )
            )

            # Predicción baseline
            fig.add_trace(
                go.Scatter(
                    x=[fecha_actual, fecha_siguiente],
                    y=[ultima, ultima],
                    mode="lines+markers",
                    name="Baseline",
                    line=dict(
                        color="#94A3B8",
                        width=2,
                        dash="dot",
                    ),
                )
            )

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#131E30",
                plot_bgcolor="#131E30",
                height=450,
                title=f"Predictive Performance · {par}",
                hovermode="x unified",
                legend=dict(orientation="h"),
                margin=dict(l=20, r=20, t=50, b=20),
                xaxis=dict(showgrid=False),
                yaxis=dict(
                    gridcolor="#263247",
                    title="Tipo de cambio",
                ),
            )

            st.plotly_chart(fig, use_container_width=True)

            st.caption(
                "La predicción corresponde a la siguiente cotización "
                "disponible. La fecha representada es orientativa."
            )

            with st.expander("Consultar todas las predicciones"):

                st.dataframe(
                    predicciones,
                    use_container_width=True,
                    hide_index=True,
                )

                st.download_button(
                    "Descargar predicciones",
                    data=predicciones.to_csv(index=False),
                    file_name="predicciones_divisas.csv",
                    mime="text/csv",
                )

    else:
        st.info("Genera las predicciones para visualizar el forecast.")

    st.divider()

    # Evaluación del modelo
    st.subheader("Model Evaluation")
    st.caption("Evaluación histórica sobre el conjunto de prueba")

    resultados = pd.read_csv(ruta_test)

    resultados["date"] = pd.to_datetime(resultados["date"])

    resultados["pair"] = (
        resultados["base"] + "/" + resultados["quote"]
    )

    par_evaluacion = st.selectbox(
        "Divisa para evaluación",
        sorted(resultados["pair"].unique()),
    )

    evaluacion = resultados[
        resultados["pair"] == par_evaluacion
    ].sort_values("date").copy()

    # Errores Random Forest
    error_ml = evaluacion["target"] - evaluacion["prediction"]

    mae_ml = error_ml.abs().mean()
    rmse_ml = (error_ml.pow(2).mean()) ** 0.5

    # Errores baseline
    error_baseline = evaluacion["target"] - evaluacion["rate"]

    mae_baseline = error_baseline.abs().mean()
    rmse_baseline = (error_baseline.pow(2).mean()) ** 0.5

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("MAE Random Forest", f"{mae_ml:.6f}")
    c2.metric("MAE Baseline", f"{mae_baseline:.6f}")
    c3.metric("RMSE Random Forest", f"{rmse_ml:.6f}")
    c4.metric("RMSE Baseline", f"{rmse_baseline:.6f}")

    # Comparación de errores
    comparacion = pd.DataFrame({
        "Métrica": ["MAE", "MAE", "RMSE", "RMSE"],
        "Modelo": [
            "Random Forest",
            "Baseline",
            "Random Forest",
            "Baseline",
        ],
        "Error": [
            mae_ml,
            mae_baseline,
            rmse_ml,
            rmse_baseline,
        ],
    })

    fig_metricas = px.bar(
        comparacion,
        x="Métrica",
        y="Error",
        color="Modelo",
        barmode="group",
        color_discrete_map={
            "Random Forest": "#A78BFA",
            "Baseline": "#36D9B3",
        },
    )

    fig_metricas.update_layout(
        template="plotly_dark",
        paper_bgcolor="#131E30",
        plot_bgcolor="#131E30",
        height=350,
        title="Model Benchmark",
        margin=dict(l=20, r=20, t=50, b=20),
        yaxis=dict(gridcolor="#263247"),
    )

    st.plotly_chart(
        fig_metricas,
        use_container_width=True,
    )

    if mae_ml < mae_baseline:

        st.success(
            "Random Forest supera al baseline en MAE "
            "para esta divisa."
        )

    elif mae_ml > mae_baseline:

        st.warning(
            "El baseline obtiene un MAE inferior al Random Forest "
            "para esta divisa. El modelo presenta margen de mejora."
        )

    else:

        st.info("Ambos modelos obtienen el mismo MAE.")

    # Comparación histórica
    st.subheader("Backtesting Performance")

    fig_test = go.Figure()

    for columna, nombre, color in [
        ("target", "Valor real siguiente", "#36D9B3"),
        ("prediction", "Random Forest", "#A78BFA"),
        ("rate", "Baseline", "#94A3B8"),
    ]:

        fig_test.add_trace(
            go.Scatter(
                x=evaluacion["date"],
                y=evaluacion[columna],
                mode="lines",
                name=nombre,
                line=dict(color=color, width=2),
            )
        )

    fig_test.update_layout(
        template="plotly_dark",
        paper_bgcolor="#131E30",
        plot_bgcolor="#131E30",
        height=450,
        hovermode="x unified",
        legend=dict(orientation="h"),
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(title="Fecha de origen de la predicción"),
        yaxis=dict(gridcolor="#263247"),
    )

    st.plotly_chart(fig_test, use_container_width=True)

    st.caption(
        "Evaluación temporal: 80 % entrenamiento y 20 % prueba. "
        "El baseline utiliza la última cotización disponible "
        "como predicción de la siguiente."
    )

    st.info(
        "Las predicciones tienen carácter experimental "
        "y no constituyen recomendaciones de inversión."
    )


# INFORMES DE IA

elif pagina == "Informe IA":

    st.header("AI Research")
    st.caption("Generative AI · Financial Intelligence")

    ruta_csv = Path(__file__).parent / "datos" / "divisas.csv"

    df = pd.read_csv(ruta_csv)
    df["date"] = pd.to_datetime(df["date"])
    df["pair"] = df["base"] + "/" + df["quote"]

    st.subheader("Research Configuration")

    col1, col2 = st.columns(2)

    with col1:

        pares = sorted(df["pair"].unique())

        seleccion = st.multiselect(
            "Divisas para analizar",
            pares,
            default=pares,
        )

        periodo = st.selectbox(
            "Periodo de análisis",
            ["1 mes", "3 meses", "6 meses", "1 año", "Todo"],
            index=3,
        )

    with col2:

        modo = st.radio(
            "Modo de ejecución",
            ["mock", "real"],
            format_func=lambda x: (
                "Simulación" if x == "mock" else "IA generativa real"
            ),
        )

        proveedor = None

        if modo == "real":

            proveedor = st.selectbox(
                "Proveedor de inteligencia artificial",
                ["nvidia", "openai"],
                format_func=lambda x: x.upper(),
            )

        else:
            st.info(
                "Modo de simulación sin consumo de APIs externas."
            )

    if not seleccion:
        st.warning("Selecciona al menos una divisa.")
        st.stop()

    filtrado = df[df["pair"].isin(seleccion)].copy()

    periodos = {
        "1 mes": 30,
        "3 meses": 90,
        "6 meses": 180,
        "1 año": 365,
    }

    if periodo != "Todo":

        fecha_limite = (
            df["date"].max()
            - pd.Timedelta(days=periodos[periodo])
        )

        filtrado = filtrado[
            filtrado["date"] >= fecha_limite
        ].copy()

    if filtrado.empty:
        st.warning("No hay datos para el periodo seleccionado.")
        st.stop()

    filtrado = filtrado.sort_values(
        ["base", "quote", "date"]
    )

    st.divider()

    # Información del análisis
    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Divisas seleccionadas",
        filtrado["pair"].nunique(),
    )

    c2.metric(
        "Registros analizados",
        f"{len(filtrado):,}",
    )

    c3.metric(
        "Motor de IA",
        proveedor.upper() if proveedor else "MOCK",
    )

    st.caption(
        f"Periodo analizado: "
        f"{filtrado['date'].min():%d/%m/%Y} - "
        f"{filtrado['date'].max():%d/%m/%Y}"
    )

    st.divider()

    # Generación del informe
    if st.button(
        "Generar informe de inteligencia financiera",
        type="primary",
    ):

        st.session_state.pop("research_result", None)

        try:

            inicio = time.perf_counter()

            with st.spinner(
                "Analizando el mercado y generando el informe..."
            ):

                config = load_config(ai_mode="mock")
                config.ai_mode = modo

                if proveedor:
                    config.ai_provider = proveedor

                datos_analisis = filtrado[
                    ["date", "base", "quote", "rate"]
                ].copy()

                datos_analisis["date"] = (
                    datos_analisis["date"].dt.strftime("%Y-%m-%d")
                )

                analyzer = ExchangeRateAnalyzer(datos_analisis)

                metricas = analyzer.generate_report()

                cliente = AIClient(config)

                informe = cliente.generate_report(metricas)

                duracion = time.perf_counter() - inicio

                st.session_state["research_result"] = {
                    "informe": informe,
                    "duracion": duracion,
                    "proveedor": proveedor or "mock",
                    "registros": len(filtrado),
                    "divisas": seleccion.copy(),
                    "periodo": periodo,
                    "fecha": pd.Timestamp.now().strftime(
                        "%d/%m/%Y %H:%M:%S"
                    ),
                }

                logger.info(
                    "Informe IA generado: proveedor=%s, "
                    "registros=%s, duracion=%.2fs",
                    proveedor or "mock",
                    len(filtrado),
                    duracion,
                )

                st.success("Informe generado correctamente.")

        except Exception:

            logger.exception("Error generando informe IA")

            st.error(
                "No se pudo generar el informe. "
                "Comprueba la configuración del proveedor."
            )

    # Visualización del informe
    if "research_result" in st.session_state:

        resultado = st.session_state["research_result"]

        st.divider()

        st.subheader("Research Report")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Proveedor utilizado",
            resultado["proveedor"].upper(),
        )

        c2.metric(
            "Tiempo de generación",
            f"{resultado['duracion']:.2f} s",
        )

        c3.metric(
            "Registros procesados",
            f"{resultado['registros']:,}",
        )

        st.caption(
            f"Informe generado: {resultado['fecha']} | "
            f"Periodo: {resultado['periodo']}"
        )

        st.caption(
            "Divisas analizadas: "
            + ", ".join(resultado["divisas"])
        )

        with st.container(border=True):

            st.markdown(resultado["informe"])

        st.download_button(
            "Descargar informe Markdown",
            data=resultado["informe"],
            file_name="divisas_ai_research.md",
            mime="text/markdown",
        )

    else:

        st.info(
            "Configura los parámetros y genera un informe "
            "para comenzar el análisis."
        )

    st.caption(
        "Los informes se generan a partir de estadísticas "
        "históricas del mercado y pueden contener errores. "
        "No constituyen recomendaciones de inversión."
    )
