# Proyecto II — Automatización e integración de servicios

## 1. Descripción

Este proyecto implementa un pipeline automatizado de procesamiento y análisis de tipos de cambio de divisas.

Es una ampliación del Proyecto I, incorporando automatización mediante CLI, un sistema de logs, configuración mediante variables de entorno e integración con servicios de inteligencia artificial.

El objetivo es procesar datos históricos de divisas, calcular métricas estadísticas y generar un informe explicativo a partir de los resultados obtenidos.

El proyecto permite ejecutar el análisis de forma reproducible, tanto sin conexión a un servicio de IA mediante el modo `mock` como utilizando un proveedor externo mediante el modo `real`.

## 2. Funcionalidades

- Lectura de datos históricos desde un archivo CSV.
- Actualización opcional de datos mediante la API de Frankfurter.
- Validación de registros utilizando Pydantic.
- Identificación de registros inválidos y duplicados.
- Limpieza y procesamiento de los datos.
- Cálculo de métricas estadísticas por par de divisas.
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

### 6.1. Ejecución con datos locales

Para procesar los datos existentes y generar un informe en modo `mock`:

```bash
uv run python -m divisas_app.cli --input datos/divisas.csv --output resultados --ai-mode mock
```

### 6.2. Actualización mediante Frankfurter

Para actualizar los datos antes de ejecutar el pipeline:

```bash
uv run python -m divisas_app.cli --update --input datos/divisas.csv --output resultados --ai-mode mock
```

Esta opción utiliza la API de Frankfurter para obtener datos de divisas.

### 6.3. Ejecución con NVIDIA Nemotron

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

El pipeline procesa los registros, calcula las métricas y envía los resultados estadísticos al modelo de NVIDIA para generar un informe explicativo en español.

El informe se guarda en:

`resultados_nvidia/informe_ia.md`

### 6.4. Ejecución con OpenAI

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
| `pipeline.log` | Registro de eventos de ejecución. |
| `informe_ia.md` | Informe explicativo generado por el cliente de IA. |

Las métricas incluyen:

- Tipo de cambio medio.
- Tipo de cambio mínimo.
- Tipo de cambio máximo.
- Número de registros.
- Variación porcentual entre el primer y el último registro.

### Resultados de la ejecución comprobada

En una ejecución real del pipeline con NVIDIA Nemotron se obtuvieron los siguientes resultados:

| Indicador | Resultado |
|---|---:|
| Registros originales | 17.966 |
| Registros válidos | 17.966 |
| Registros inválidos | 0 |
| Registros duplicados | 0 |
| Registros limpios | 17.966 |
| Pares de divisas analizados | 13 |

La petición a NVIDIA se completó correctamente y el informe se guardó en `resultados_nvidia/informe_ia.md`.

Se comprobó que las primeras cinco filas de las métricas del CSV coincidían con los valores presentados en el informe, considerando el redondeo decimal.

## 8. Integración de inteligencia artificial

La integración de inteligencia artificial se encuentra en:

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

La inteligencia artificial se utiliza para explicar los resultados obtenidos, no para calcular las métricas originales ni predecir tipos de cambio futuros.

### Validación de la integración

La integración con NVIDIA se ha comprobado mediante una ejecución real de la API.

El pipeline consiguió enviar las métricas, recibir una respuesta y guardar el informe generado.

Además, se incluyen pruebas automatizadas que simulan las respuestas de los proveedores para verificar el funcionamiento del cliente sin depender de servicios externos.

## 9. Pruebas automatizadas

El proyecto incluye **27 pruebas automatizadas** con pytest.

Para ejecutar todos los tests:

```bash
uv run pytest -v
```

Para obtener un resultado resumido:

```bash
uv run pytest -q
```

Las pruebas cubren diferentes componentes del sistema:

- Validación de registros.
- Procesamiento y limpieza de datos.
- Cálculo de métricas.
- Actualización de datos.
- Generación de informes en modo mock.
- Generación de informes mediante clientes de IA simulados.
- Comprobación de errores y ausencia de credenciales.
- Funcionamiento integrado del pipeline.

Las llamadas externas se simulan en los tests correspondientes para evitar depender de la disponibilidad de servicios externos durante las pruebas.

### Comprobación de calidad del código

Para ejecutar Ruff:

```bash
uv run ruff check .
```

Durante la revisión del proyecto se ejecutó la batería de pruebas y se obtuvieron 27 tests superados.

## 10. Arquitectura

El pipeline sigue el siguiente flujo:

1. Lectura de datos desde CSV y actualización opcional mediante Frankfurter.
2. Validación de los registros con Pydantic.
3. Identificación y eliminación de duplicados.
4. Cálculo de métricas estadísticas.
5. Generación del informe mediante el cliente de IA.
6. Exportación de archivos CSV, informe Markdown y logs.

El sistema está dividido en módulos independientes para facilitar su mantenimiento, reutilización y pruebas.

La separación entre procesamiento de datos y generación de informes permite ejecutar el pipeline sin depender obligatoriamente de un proveedor externo de inteligencia artificial.

## 11. Limitaciones

- La actualización de datos depende de la disponibilidad de la API de Frankfurter.
- El modo real requiere conexión a Internet y credenciales válidas.
- Los proveedores externos pueden aplicar límites de uso o restricciones de acceso.
- Los informes generados por IA pueden contener errores de interpretación o redondeo.
- La comprobación manual de las cifras del informe de NVIDIA se ha realizado sobre las primeras cinco filas de métricas, no sobre la totalidad de los valores.
- Las métricas históricas no garantizan comportamientos futuros.
- La integración real con NVIDIA ha sido validada mediante una petición auténtica.
- La integración con OpenAI cuenta con pruebas automatizadas, pero no se ha comprobado mediante una petición real.

## 12. Uso de herramientas de IA

El archivo `AI_USAGE.md` documenta el uso de herramientas de inteligencia artificial durante el desarrollo del proyecto.

Incluye información sobre la asistencia recibida, las tareas realizadas, las comprobaciones efectuadas y las limitaciones asociadas al uso de estas herramientas.

El procesamiento de datos, el cálculo de métricas y la ejecución del pipeline se realizan mediante código Python. La inteligencia artificial externa se utiliza para generar el informe explicativo a partir de los resultados calculados.