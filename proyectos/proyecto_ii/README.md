# Proyecto II — Automatización e integración de servicios

## 1. Descripción

Este proyecto implementa un pipeline automatizado de procesamiento, análisis y predicción de tipos de cambio de divisas.

Es una ampliación del Proyecto I, incorporando automatización mediante CLI, un sistema de logs, configuración mediante variables de entorno, entrenamiento de modelos de Machine Learning con scikit-learn e integración con servicios externos de inteligencia artificial.

El objetivo es procesar datos históricos de divisas, calcular métricas estadísticas, entrenar modelos predictivos y generar un informe explicativo a partir de los resultados obtenidos.

El proyecto permite ejecutar el análisis de forma reproducible, tanto sin conexión a un servicio externo de IA mediante el modo `mock` como utilizando un proveedor externo mediante el modo `real`.

## 2. Funcionalidades

- Lectura de datos históricos desde un archivo CSV.
- Actualización opcional de datos mediante la API de Frankfurter.
- Validación de registros utilizando Pydantic.
- Identificación de registros inválidos y duplicados.
- Limpieza y procesamiento de los datos.
- Cálculo de métricas estadísticas por par de divisas.
- Entrenamiento de modelos Random Forest con scikit-learn.
- Persistencia y carga de modelos mediante joblib.
- Predicción del siguiente tipo de cambio por par de divisas.
- Evaluación de los modelos mediante MAE y RMSE.
- Comparación de los resultados con un modelo baseline.
- Exportación de resultados a archivos CSV.
- Registro de eventos y errores mediante logs.
- Generación de informes explicativos mediante inteligencia artificial.
- Integración con NVIDIA Nemotron y OpenAI.
- Ejecución en modo `mock` o `real`.
- Configuración mediante variables de entorno.
- Pruebas automatizadas con pytest.

## 3. Tecnologías utilizadas

- **Python:** lenguaje principal del proyecto.
- **pandas:** procesamiento y análisis de datos.
- **scikit-learn:** entrenamiento y evaluación de modelos predictivos.
- **RandomForestRegressor:** algoritmo utilizado para predecir tipos de cambio.
- **joblib:** almacenamiento y carga de modelos entrenados.
- **Pydantic:** validación de registros.
- **requests:** comunicación con la API de Frankfurter.
- **OpenAI SDK:** cliente utilizado para conectar con APIs compatibles, incluida NVIDIA.
- **NVIDIA Nemotron:** modelo de inteligencia artificial utilizado para generar informes.
- **python-dotenv:** gestión de variables de entorno.
- **pytest:** pruebas automatizadas.
- **Ruff:** análisis estático y comprobación del código.
- **uv:** gestión de dependencias y ejecución del proyecto.
- **Git y GitHub:** control de versiones.

## 4. Instalación

Clonar el repositorio:

```bash
git clone https://github.com/alvarofernandezsanchez/dsia-26-27-FernandezAlvaro.git
```

Acceder al proyecto:

```bash
cd dsia-26-27-FernandezAlvaro
git switch feature/proyecto-ii
cd proyectos/proyecto_ii
```

Instalar las dependencias:

```bash
uv sync
```

Como alternativa, se incluye un archivo `requirements.txt` para instalar las dependencias mediante pip dentro de un entorno virtual.

Las dependencias incluyen `scikit-learn` y `joblib`, necesarias para entrenar, guardar y utilizar los modelos predictivos.

## 5. Configuración

El proyecto utiliza variables de entorno para gestionar los modos de ejecución, los proveedores de inteligencia artificial y las credenciales.

Crear un archivo `.env` a partir de `.env.example`.

Ejemplo de configuración:

```dotenv
AI_MODE=mock
AI_PROVIDER=nvidia

NVIDIA_API_KEY=
NVIDIA_MODEL=nvidia/nemotron-3.5-super-vl-120b-a12b

OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini

LOG_LEVEL=INFO
```

### Variables principales

| Variable | Descripción |
|---|---|
| `AI_MODE` | Modo de generación del informe: `mock` o `real`. |
| `AI_PROVIDER` | Proveedor de IA: `nvidia` u `openai`. |
| `NVIDIA_API_KEY` | Clave personal para acceder a NVIDIA. |
| `NVIDIA_MODEL` | Identificador del modelo de NVIDIA. |
| `OPENAI_API_KEY` | Clave personal para acceder a OpenAI. |
| `OPENAI_MODEL` | Identificador del modelo de OpenAI. |
| `LOG_LEVEL` | Nivel de registro de eventos. |

El modo `mock` no necesita una clave de API y permite ejecutar el pipeline sin realizar peticiones a servicios externos de inteligencia artificial.

Para utilizar el modo `real`, es necesario configurar una clave válida del proveedor seleccionado.

**Importante:** el archivo `.env` contiene credenciales personales y no debe subirse al repositorio. El archivo `.env.example` permite mostrar la configuración necesaria sin incluir claves privadas.

## 6. Ejecución

### 6.1. Entrenamiento del modelo sklearn

Antes de ejecutar las predicciones, es necesario entrenar el modelo.

```bash
uv run python -m divisas_app.train
```

El entrenamiento utiliza los datos históricos almacenados en `datos/divisas.csv`.

Se entrena un modelo `RandomForestRegressor` independiente para cada par de divisas, utilizando las siguientes variables:

- `rate`: tipo de cambio actual.
- `rate_lag_1`: tipo de cambio anterior.
- `rate_lag_2`: tipo de cambio de dos registros anteriores.
- `rate_lag_3`: tipo de cambio de tres registros anteriores.

La variable objetivo (`target`) es el tipo de cambio del siguiente registro.

Los datos se dividen cronológicamente en un 80 % para entrenamiento y un 20 % para evaluación.

Los modelos entrenados se guardan en:

`modelos/divisas_model.joblib`

También se generan archivos con las métricas y las predicciones de evaluación:

- `modelos/metricas_modelo.csv`
- `modelos/predicciones_test.csv`

El archivo `divisas_model.joblib` no se incluye en GitHub debido a su tamaño, aproximadamente 128 MB. Para reproducir las predicciones, es necesario ejecutar el entrenamiento.

### 6.2. Ejecución con datos locales

Para procesar los datos existentes, generar las predicciones de sklearn y crear un informe en modo `mock`:

```bash
uv run python -m divisas_app.cli --input datos/divisas.csv --output resultados --ai-mode mock
```

El pipeline carga el modelo entrenado y genera un archivo adicional:

`resultados/predicciones_sklearn.csv`

Este archivo contiene las predicciones del siguiente tipo de cambio para los pares de divisas disponibles.

Si el archivo del modelo no existe, el pipeline registra una advertencia y continúa con el análisis estadístico y la generación del informe.

### 6.3. Actualización mediante Frankfurter

Para actualizar los datos antes de ejecutar el pipeline:

```bash
uv run python -m divisas_app.cli --update --input datos/divisas.csv --output resultados --ai-mode mock
```

Esta opción utiliza la API de Frankfurter para obtener datos de divisas.

Si se incorporan nuevas observaciones al conjunto de datos, es recomendable volver a entrenar los modelos.

### 6.4. Ejecución con NVIDIA Nemotron

Para generar un informe utilizando la API real de NVIDIA, configurar previamente:

```dotenv
AI_PROVIDER=nvidia
AI_MODE=real
NVIDIA_API_KEY=TU_CLAVE_PERSONAL
NVIDIA_MODEL=nvidia/nemotron-3.5-super-vl-120b-a12b
```

Después ejecutar:

```bash
uv run python -m divisas_app.cli --input datos/divisas.csv --output resultados_nvidia --ai-mode real
```

El pipeline procesa los registros, calcula las métricas, genera las predicciones de sklearn y envía los resultados estadísticos al modelo de NVIDIA para generar un informe explicativo en español.

El informe se guarda en:

`resultados_nvidia/informe_ia.md`

### 6.5. Ejecución con OpenAI

El cliente también contempla el proveedor OpenAI.

Para seleccionarlo, configurar:

```dotenv
AI_PROVIDER=openai
AI_MODE=real
OPENAI_API_KEY=TU_CLAVE_PERSONAL
OPENAI_MODEL=gpt-4.1-mini
```

Ejecutar:

```bash
uv run python -m divisas_app.cli --input datos/divisas.csv --output resultados_openai --ai-mode real
```

La integración de OpenAI dispone de pruebas automatizadas con respuestas simuladas. No se ha validado mediante una petición real durante las comprobaciones de esta entrega.

**Nota:** las peticiones a proveedores externos pueden estar sujetas a límites de uso, créditos disponibles o costes asociados.

## 7. Resultados generados

El pipeline genera los siguientes archivos en el directorio de salida seleccionado:

| Archivo | Descripción |
|---|---|
| `divisas_limpias.csv` | Registros válidos sin duplicados. |
| `registros_invalidos.csv` | Registros que no superan la validación. |
| `duplicados.csv` | Registros duplicados detectados. |
| `metricas_divisas.csv` | Estadísticas calculadas por par de divisas. |
| `predicciones_sklearn.csv` | Predicciones realizadas por los modelos sklearn. |
| `pipeline.log` | Registro de eventos de ejecución. |
| `informe_ia.md` | Informe explicativo generado por el cliente de IA. |

Las métricas estadísticas incluyen:

- Tipo de cambio medio.
- Tipo de cambio mínimo.
- Tipo de cambio máximo.
- Número de registros.
- Variación porcentual entre el primer y el último registro.

### Resultados de la ejecución comprobada

En la ejecución del pipeline con sklearn y el modo de IA `mock` se obtuvieron los siguientes resultados:

| Indicador | Resultado |
|---|---:|
| Registros originales | 17.966 |
| Registros válidos | 17.966 |
| Registros inválidos | 0 |
| Registros duplicados | 0 |
| Registros limpios | 17.966 |
| Pares de divisas analizados | 13 |
| Predicciones sklearn generadas | 13 |

El pipeline finalizó correctamente, cargó los modelos entrenados y generó el informe explicativo.

También se realizó una ejecución real con NVIDIA Nemotron, en la que la petición a la API se completó correctamente y se guardó el informe correspondiente.

## 8. Modelo predictivo con scikit-learn

### 8.1. Objetivo

El objetivo del modelo es predecir el siguiente tipo de cambio de cada par de divisas utilizando información histórica.

Se utiliza un enfoque de aprendizaje supervisado mediante regresión.

### 8.2. Algoritmo seleccionado

Se ha utilizado `RandomForestRegressor`, disponible en scikit-learn.

Este algoritmo combina múltiples árboles de decisión para realizar predicciones numéricas.

Se ha seleccionado porque permite trabajar con relaciones no lineales y ofrece una implementación sencilla y reproducible.

Los parámetros principales utilizados son:

- `n_estimators=100`
- `random_state=42`
- `n_jobs=-1`

Se entrena un modelo independiente para cada par de divisas, evitando mezclar directamente tipos de cambio con escalas diferentes.

### 8.3. Preparación de los datos

Los registros se ordenan por par de divisas y fecha.

Posteriormente, se generan variables históricas mediante desplazamientos temporales (`lags`).

Se eliminan los registros que no contienen suficiente historial o que no tienen un valor objetivo disponible.

La separación entre entrenamiento y evaluación se realiza respetando el orden temporal.

### 8.4. Evaluación del modelo

Para evaluar las predicciones se utilizan las siguientes métricas:

- **MAE (Mean Absolute Error):** error absoluto medio entre los valores reales y los predichos.
- **RMSE (Root Mean Squared Error):** raíz del error cuadrático medio, que penaliza más los errores grandes.
- **Baseline MAE:** error de una predicción sencilla que utiliza el último tipo de cambio conocido como estimación del siguiente.

Los resultados obtenidos durante el entrenamiento fueron:

| Métrica | Resultado |
|---|---:|
| MAE | 0,557500 |
| RMSE | 2,244938 |
| Baseline MAE | 0,083227 |
| Modelos entrenados | 13 |
| Registros de entrenamiento | 14.326 |
| Registros de evaluación | 3.588 |

Los resultados muestran que el modelo Random Forest presenta un error absoluto medio superior al baseline.

Esto significa que, con la configuración actual, el modelo entrenado no mejora la predicción sencilla basada en mantener el último valor conocido.

Por tanto, **no se considera un modelo suficientemente preciso para su utilización en decisiones financieras reales**.

La evaluación permite identificar esta limitación y establecer mejoras para futuras versiones.

Además, las métricas globales combinan pares de divisas con escalas distintas, por lo que sería conveniente evaluar cada par por separado.

### 8.5. Persistencia e inferencia

Los modelos se guardan utilizando `joblib` en el archivo:

`modelos/divisas_model.joblib`

El módulo `sklearn_inference.py` permite cargar los modelos entrenados y generar predicciones sin necesidad de volver a entrenarlos en cada ejecución.

La integración se realiza desde `main.py`, después de validar, limpiar y analizar los datos.

Las predicciones se exportan automáticamente a `predicciones_sklearn.csv`.

## 9. Integración de inteligencia artificial externa

La integración de inteligencia artificial generativa se encuentra en:

`src/divisas_app/ai_client.py`

El cliente admite dos modos de funcionamiento.

### Modo mock

Genera un informe local y determinista a partir de las métricas calculadas.

Sus principales características son:

- No requiere credenciales.
- No realiza peticiones externas de IA.
- Permite realizar pruebas reproducibles.
- Facilita la ejecución del proyecto por parte de otros usuarios.

### Modo real

Utiliza un servicio externo de inteligencia artificial para generar un informe en español a partir de las métricas estadísticas.

El cliente permite seleccionar entre dos proveedores:

**NVIDIA:** conexión mediante una API compatible con el SDK de OpenAI, utilizando el endpoint `https://integrate.api.nvidia.com/v1`.

**OpenAI:** conexión mediante el cliente oficial de OpenAI.

El proveedor se selecciona mediante la variable `AI_PROVIDER`.

### Modelo NVIDIA utilizado

`nvidia/nemotron-3.5-super-vl-120b-a12b`

El modelo recibe las métricas calculadas y genera un informe en formato Markdown.

Las instrucciones enviadas al modelo establecen que debe:

- Redactar el informe en español.
- Utilizar únicamente las cifras proporcionadas.
- Evitar inventar datos o causas económicas.
- No realizar predicciones.
- No proporcionar recomendaciones de inversión.

Es importante distinguir los dos componentes de inteligencia artificial del proyecto:

- **scikit-learn:** realiza predicciones numéricas de tipos de cambio mediante modelos entrenados localmente.
- **NVIDIA Nemotron/OpenAI:** genera explicaciones en lenguaje natural a partir de las métricas estadísticas.

La inteligencia artificial generativa no sustituye al modelo predictivo ni calcula las métricas originales.

Se ha elegido NVIDIA Nemotron como proveedor alternativo a Hugging Face, conforme a las opciones permitidas en el enunciado. Su tarea es la generación de informes explicativos en lenguaje natural a partir de las métricas del pipeline.

### Validación de la integración

La integración con NVIDIA se ha comprobado mediante una ejecución real de la API.

El pipeline consiguió enviar las métricas, recibir una respuesta y guardar el informe generado.

Además, se incluyen pruebas automatizadas que simulan las respuestas de los proveedores para verificar el funcionamiento del cliente sin depender de servicios externos.

## 10. Pruebas automatizadas

El proyecto incluye **31 pruebas automatizadas** con pytest.

Para ejecutar todos los tests:

```bash
uv run pytest -v
```

Para obtener un resultado resumido:

```bash
uv run pytest -q
```

Durante la última comprobación se obtuvo:

```text
31 passed in 8.57s
```

Las pruebas cubren:

- Validación de registros.
- Procesamiento y limpieza de datos.
- Cálculo de métricas.
- Actualización de datos.
- Generación de informes en modo mock.
- Generación de informes mediante clientes de IA simulados.
- Comprobación de errores y ausencia de credenciales.
- Funcionamiento integrado del pipeline.
- Preparación de variables históricas para sklearn.
- Entrenamiento y almacenamiento de modelos.
- Carga de modelos mediante joblib.
- Inferencia y generación de predicciones.

Las llamadas externas se simulan en los tests correspondientes para evitar depender de la disponibilidad de servicios externos durante las pruebas.

### Comprobación de calidad del código

Para ejecutar Ruff:

```bash
uv run ruff check .
```

La comprobación de calidad del código se completó correctamente.

## 11. Arquitectura

El pipeline sigue el siguiente flujo:

1. Lectura de datos desde CSV y actualización opcional mediante Frankfurter.
2. Validación de los registros con Pydantic.
3. Identificación y eliminación de duplicados.
4. Cálculo de métricas estadísticas.
5. Carga de los modelos sklearn previamente entrenados.
6. Generación de predicciones por par de divisas.
7. Generación del informe explicativo mediante el cliente de IA.
8. Exportación de archivos CSV, informe Markdown y logs.

El entrenamiento se ejecuta mediante un módulo independiente, `train.py`, que prepara los datos, entrena los modelos, calcula las métricas de evaluación y guarda los modelos utilizando joblib.

El sistema está dividido en módulos independientes para facilitar su mantenimiento, reutilización y pruebas.

La separación entre procesamiento de datos, predicción con Machine Learning y generación de informes permite utilizar cada componente de forma independiente.

## 12. Datos utilizados

El proyecto utiliza datos históricos de tipos de cambio obtenidos mediante la API pública **Frankfurter**.

**Fuente:** https://frankfurter.dev/

**Endpoint utilizado:** `https://api.frankfurter.dev/v2/rates.csv`

El conjunto de datos contiene información histórica desde 2023 y se almacena localmente en:

`datos/divisas.csv`

Durante el desarrollo del proyecto, el dataset se actualizó mediante la API de Frankfurter, pasando de 14.248 a 17.966 registros.

Las columnas utilizadas son:

| Columna | Descripción |
|---|---|
| `date` | Fecha de la observación. |
| `base` | Moneda base. |
| `quote` | Moneda de cotización. |
| `rate` | Tipo de cambio registrado. |

El conjunto utilizado contiene **17.966 registros correspondientes a 13 pares de divisas**.

### Motivación de la elección del dataset

Se ha seleccionado este conjunto de datos porque permite trabajar con información financiera histórica organizada temporalmente, aplicar procesos de validación y limpieza, calcular métricas estadísticas y desarrollar modelos de predicción.

Además, la disponibilidad de una API pública facilita la automatización de la actualización de los datos.

### Licencia y condiciones de uso

Los datos históricos de tipos de cambio se obtienen mediante la API pública Frankfurter (https://frankfurter.dev/).

Frankfurter distribuye su software bajo licencia MIT. Sin embargo, esta licencia no se aplica automáticamente a los datos, que proceden de bancos centrales y otras instituciones.

Las condiciones de reutilización dependen de los proveedores originales de los datos.

Documentación: https://frankfurter.dev/license/

Los datos se utilizan en este proyecto con fines académicos, para realizar análisis estadísticos y entrenar modelos predictivos.

## 13. Limitaciones

- La actualización de datos depende de la disponibilidad de la API de Frankfurter.
- El modo real requiere conexión a Internet y credenciales válidas.
- Los proveedores externos pueden aplicar límites de uso o restricciones de acceso.
- Los informes generados por IA pueden contener errores de interpretación o redondeo.
- La comprobación manual de las cifras del informe de NVIDIA se realizó sobre las primeras cinco filas de métricas.
- Las métricas históricas no garantizan comportamientos futuros.
- El modelo Random Forest presenta un MAE superior al baseline en la evaluación realizada.
- La evaluación global combina pares de divisas con diferentes escalas.
- El modelo utiliza únicamente información histórica del tipo de cambio, sin incorporar variables macroeconómicas.
- El modelo debe volver a entrenarse cuando se desee actualizarlo con nuevos datos.
- La integración con OpenAI cuenta con pruebas automatizadas, pero no se ha comprobado mediante una petición real.

## 14. Uso de herramientas de IA

El archivo `AI_USAGE.md` documenta el uso de herramientas de inteligencia artificial durante el desarrollo del proyecto.

Incluye información sobre la asistencia recibida, las tareas realizadas, las comprobaciones efectuadas y las limitaciones asociadas al uso de estas herramientas.

El procesamiento de datos, el cálculo de métricas, el entrenamiento de sklearn y la ejecución del pipeline se realizan mediante código Python.

La inteligencia artificial externa se utiliza para generar el informe explicativo a partir de los resultados estadísticos calculados.

## 15. Continuación hacia el Proyecto III

El Proyecto II establece una base funcional para continuar desarrollando el sistema en el Proyecto III.

Las principales líneas de mejora previstas son:

- Mejorar el rendimiento predictivo de los modelos sklearn.
- Comparar Random Forest con otros algoritmos de regresión.
- Evaluar los modelos individualmente por par de divisas.
- Incorporar nuevas variables temporales y económicas.
- Automatizar el reentrenamiento cuando se incorporen nuevos datos.
- Mejorar la gestión de versiones de los modelos.
- Ampliar la observabilidad del pipeline.
- Incorporar una interfaz que permita consultar métricas, predicciones e informes.

Estas mejoras permitirían evolucionar el proyecto desde un pipeline automatizado hacia una aplicación de análisis y predicción de divisas más completa.