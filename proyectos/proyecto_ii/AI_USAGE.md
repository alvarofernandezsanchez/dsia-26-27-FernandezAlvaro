# AI_USAGE — Proyecto II

## 1. Herramientas de IA utilizadas

Durante el desarrollo del Proyecto II se ha utilizado **ChatGPT (OpenAI)** como herramienta de apoyo para la programación, la explicación de conceptos, la depuración de errores, la preparación de pruebas y la elaboración de documentación.

Además, el proyecto incorpora dos componentes relacionados con la inteligencia artificial:

- **Machine Learning con scikit-learn:** entrenamiento de modelos Random Forest para predecir tipos de cambio de divisas.
- **Inteligencia artificial generativa:** integración con servicios externos para generar informes explicativos a partir de las métricas estadísticas calculadas.

Para la generación de informes se han contemplado dos proveedores:

- **NVIDIA Nemotron:** proveedor utilizado y validado mediante una petición real a su API.
- **OpenAI:** proveedor alternativo implementado y comprobado mediante pruebas automatizadas con respuestas simuladas.

## 2. Uso de IA durante el desarrollo

ChatGPT se ha utilizado como apoyo para:

- Diseñar la estructura del pipeline y su integración con servicios externos.
- Implementar el sistema de logs y la configuración mediante variables de entorno.
- Desarrollar el cliente de IA con los modos `mock` y `real`.
- Incorporar la selección entre los proveedores NVIDIA y OpenAI.
- Diseñar el proceso de entrenamiento de modelos con scikit-learn.
- Preparar las variables históricas utilizadas para predecir tipos de cambio.
- Implementar el entrenamiento mediante `RandomForestRegressor`.
- Incorporar el almacenamiento y la carga de modelos utilizando `joblib`.
- Integrar las predicciones de sklearn en el pipeline principal.
- Preparar pruebas unitarias y de integración mediante `pytest`.
- Identificar y corregir errores durante la ejecución.
- Interpretar las métricas MAE, RMSE y baseline.
- Elaborar y actualizar la documentación técnica del proyecto.

El código se ha integrado y comprobado localmente mediante ejecuciones del pipeline y pruebas automatizadas.

La utilización de ChatGPT ha servido como apoyo al desarrollo. Las funcionalidades implementadas se han contrastado mediante pruebas y ejecuciones del programa.

## 3. Integración de IA en el proyecto

### 3.1. Machine Learning con scikit-learn

Se ha incorporado un sistema de predicción de tipos de cambio mediante modelos de aprendizaje supervisado.

El entrenamiento se implementa en:

`src/divisas_app/train.py`

Se utiliza el algoritmo `RandomForestRegressor` de scikit-learn.

Los modelos emplean las siguientes variables:

- `rate`: tipo de cambio actual.
- `rate_lag_1`: tipo de cambio anterior.
- `rate_lag_2`: tipo de cambio de dos registros anteriores.
- `rate_lag_3`: tipo de cambio de tres registros anteriores.

La variable objetivo es el tipo de cambio del siguiente registro.

Se entrena un modelo independiente para cada par de divisas.

Los modelos se guardan mediante `joblib` en:

`modelos/divisas_model.joblib`

El módulo `sklearn_inference.py` permite cargar los modelos y generar predicciones sin repetir el entrenamiento.

Las predicciones se integran en `main.py` y se exportan a:

`resultados/predicciones_sklearn.csv`

### 3.2. Evaluación de los modelos

Durante el entrenamiento se utilizan las métricas MAE y RMSE para evaluar el rendimiento predictivo.

También se compara el modelo con un baseline que utiliza el último tipo de cambio conocido como predicción del siguiente.

Los resultados obtenidos fueron:

| Métrica | Resultado |
|---|---:|
| MAE | 0,557500 |
| RMSE | 2,244938 |
| Baseline MAE | 0,083227 |
| Modelos entrenados | 13 |
| Registros de entrenamiento | 14.326 |
| Registros de evaluación | 3.588 |

Los resultados muestran que el modelo Random Forest obtiene un error superior al baseline.

Por tanto, aunque el entrenamiento y la integración funcionan correctamente, el modelo todavía necesita mejoras para ofrecer predicciones competitivas.

Esta limitación se ha documentado en el README.

### 3.3. Inteligencia artificial generativa

El archivo `src/divisas_app/ai_client.py` implementa dos modos de funcionamiento.

**Modo mock**

Genera un informe determinista a partir de las métricas calculadas, sin realizar peticiones a servicios externos.

Este modo permite:

- Ejecutar el pipeline sin credenciales.
- Obtener resultados reproducibles.
- Realizar pruebas automatizadas sin depender de una API externa.

**Modo real**

Permite generar un informe mediante un proveedor externo de inteligencia artificial.

El cliente admite los proveedores NVIDIA y OpenAI, seleccionados mediante la variable de entorno `AI_PROVIDER`.

La integración con NVIDIA utiliza el SDK de OpenAI, compatible con el endpoint de NVIDIA:

`https://integrate.api.nvidia.com/v1`

El modelo utilizado durante la validación ha sido:

`nvidia/nemotron-3.5-super-vl-120b-a12b`

El cliente envía al modelo las métricas estadísticas calculadas previamente por el pipeline y solicita un informe explicativo en español, en formato Markdown.

Las instrucciones enviadas al modelo establecen que debe utilizar únicamente las cifras recibidas, sin inventar causas económicas, realizar predicciones ni proporcionar recomendaciones de inversión.

El modo de funcionamiento se configura mediante `AI_MODE` en el archivo `.env` o mediante el argumento `--ai-mode` del CLI.

Las credenciales se almacenan en variables de entorno y no deben incorporarse al código fuente ni subirse al repositorio.

## 4. Validación y pruebas realizadas

Se han desarrollado pruebas automatizadas para comprobar el funcionamiento del pipeline, los modelos sklearn y el cliente de inteligencia artificial.

La batería de pruebas incluye:

- Comprobaciones del modo `mock`.
- Simulación de respuestas del proveedor OpenAI.
- Simulación de respuestas del proveedor NVIDIA.
- Comprobación de errores relacionados con la ausencia de credenciales.
- Pruebas del funcionamiento integrado del pipeline.
- Preparación de datos para el entrenamiento de sklearn.
- Entrenamiento y almacenamiento de modelos.
- Carga de modelos mediante joblib.
- Generación de predicciones mediante sklearn.

Durante la última revisión del proyecto se ejecutaron **31 pruebas automatizadas, todas superadas y sin warnings**.

El comando utilizado fue:

```bash
uv run pytest -q
```

Resultado:

```text
31 passed in 8.57s
```

También se ejecutó el entrenamiento:

```bash
uv run python -m divisas_app.train
```

Se generaron correctamente 13 modelos predictivos.

Posteriormente, se ejecutó el pipeline completo:

```bash
uv run python -m divisas_app.cli --input datos/divisas.csv --output resultados --ai-mode mock
```

El pipeline procesó 17.966 registros, cargó los modelos sklearn, generó 13 predicciones y guardó el informe explicativo.

### 4.1. Validación real con NVIDIA

Además de las pruebas simuladas, se realizó una ejecución real del pipeline utilizando NVIDIA Nemotron.

La ejecución procesó correctamente:

- 17.966 registros originales.
- 17.966 registros válidos.
- 0 registros inválidos.
- 0 registros duplicados.
- 13 pares de divisas.

El sistema calculó las métricas, realizó una petición a la API de NVIDIA y recibió un informe en formato Markdown.

El informe generado se guardó correctamente en:

`resultados_nvidia/informe_ia.md`

Se revisó el contenido del informe y se compararon las primeras cinco filas de métricas con los valores originales del archivo CSV, comprobando su coincidencia teniendo en cuenta el redondeo decimal.

Por tanto, la integración con NVIDIA se ha validado tanto mediante pruebas automatizadas con respuestas simuladas como mediante una petición real.

La integración con OpenAI dispone de pruebas automatizadas, pero no se ha validado mediante una petición auténtica a su API.

## 5. Limitaciones y responsabilidades

El uso de inteligencia artificial presenta algunas limitaciones:

- Los modelos generativos pueden producir interpretaciones incorrectas o información que no esté respaldada por los datos.
- Las cifras presentadas en los informes pueden aparecer redondeadas.
- La comprobación manual realizada sobre el informe de NVIDIA no abarca todos los valores generados.
- El acceso a las APIs externas depende de su disponibilidad, las credenciales y los límites de uso.
- Las respuestas de un modelo generativo pueden variar entre ejecuciones.
- Los resultados históricos de divisas no permiten garantizar comportamientos futuros.
- El modelo Random Forest presenta un error superior al baseline en la evaluación realizada.
- El modelo predictivo utiliza únicamente información histórica de tipos de cambio.
- Las métricas globales combinan pares de divisas con diferentes escalas.
- El modelo necesita volver a entrenarse para incorporar nuevos datos históricos.

Los informes generados no constituyen asesoramiento financiero.

La responsabilidad de revisar el código, comprobar los resultados y validar el funcionamiento del proyecto corresponde al desarrollador.

## 6. Conclusión

La inteligencia artificial se ha utilizado en tres ámbitos diferenciados:

1. Como herramienta de apoyo durante el desarrollo del proyecto mediante ChatGPT.
2. Como sistema predictivo local mediante modelos Random Forest entrenados con scikit-learn.
3. Como servicio externo de inteligencia artificial generativa mediante NVIDIA Nemotron y OpenAI.

El pipeline realiza la lectura, validación, limpieza y análisis estadístico de los datos mediante código Python.

Los modelos sklearn permiten generar predicciones numéricas, mientras que el cliente de inteligencia artificial generativa utiliza las métricas calculadas para elaborar un informe explicativo.

La implementación permite trabajar sin conexión a un proveedor externo de IA mediante el modo `mock` y generar informes mediante NVIDIA u OpenAI en el modo `real`.

La conexión real con NVIDIA Nemotron se ha comprobado satisfactoriamente.

El entrenamiento, la inferencia y el funcionamiento general del pipeline se han verificado mediante **31 pruebas automatizadas superadas**.

El sistema constituye una base funcional para continuar mejorando la precisión de los modelos y ampliar sus capacidades en el Proyecto III.