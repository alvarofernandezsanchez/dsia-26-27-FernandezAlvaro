# Proyecto II — Automatización e integración de servicios (20 %)

**Temas:** 2, 3 y 4  
**Trabajo continuo:** octubre 2026  
**Hito de presentación del Trabajo Final (enunciado E2E):** 20 de octubre de 2026

## Objetivo

Automatizar un proceso de datos e integrar al menos un **servicio de IA vía API**, con pruebas y buenas prácticas de entornos.

## Requisitos mínimos

1. Pipeline reproducible (CLI o job) con logs.
2. Tests pytest (unitarios + al menos un test de integración o marcado).
3. Cliente de IA con modo `mock` y un proveedor real documentado (si no hay clave, mock + diseño listo).
4. `.env.example` y `requirements.txt`.
5. Sección `AI_USAGE.md` citando herramientas de IA usadas en el desarrollo.

## Entrega

Repo GitHub con historial de commits a lo largo de octubre.

## Rúbrica orientativa

| Criterio | Peso |
| --- | --- |
| Pipeline y automatización | 25 % |
| Integración API / IA | 25 % |
| Tests y calidad | 20 % |
| Robustez (errores, logs, config) | 15 % |
| Documentación y citación IA | 15 % |



# Proyecto II — Automatización e integración de servicios

## 1. Descripción

Este proyecto implementa un pipeline automatizado de procesamiento y análisis de tipos de cambio de divisas.

Es una ampliación del Proyecto I, incorporando automatización mediante CLI, un sistema de logs, configuración mediante variables de entorno e integración con un servicio de inteligencia artificial.

El objetivo es procesar datos de divisas, calcular métricas estadísticas y generar un informe explicativo a partir de los resultados.

## 2. Funcionalidades

- Lectura de datos históricos desde un archivo CSV.
- Actualización de datos mediante la API de Frankfurter.
- Validación de registros utilizando Pydantic.
- Identificación de registros inválidos y duplicados.
- Cálculo de métricas estadísticas por par de divisas.
- Exportación de resultados a archivos CSV.
- Registro de eventos mediante logs.
- Generación de informes mediante un cliente de IA.
- Ejecución en modo `mock` o `real`.
- Pruebas automatizadas con pytest.

## 3. Tecnologías utilizadas

- Python
- pandas
- Pydantic
- requests
- OpenAI API
- python-dotenv
- pytest
- uv

## 4. Instalación

Clonar el repositorio y acceder a la carpeta del proyecto:

```bash
git clone https://github.com/alvarofernandezsanchez/dsia-26-27-FernandezAlvaro.git
cd dsia-26-27-FernandezAlvaro
git switch feature/proyecto-ii
cd proyectos/proyecto_ii
```

Instalar las dependencias:

```bash
uv sync
```

Como alternativa, se incluye `requirements.txt` para instalar las dependencias con pip en un entorno virtual.

## 5. Configuración

Crear un archivo `.env` a partir de `.env.example`.

Ejemplo:

```dotenv
AI_MODE=mock
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
LOG_LEVEL=INFO
```

El modo `mock` permite ejecutar el proyecto sin necesidad de utilizar una API externa de inteligencia artificial.

Para utilizar el modo `real`, es necesario configurar una clave válida de OpenAI.

El archivo `.env` no debe subirse al repositorio.

## 6. Ejecución

Ejecutar el pipeline utilizando los datos locales:

```bash
uv run python -m divisas_app.cli --input datos/divisas.csv --output resultados --ai-mode mock
```

Actualizar los datos mediante Frankfurter y ejecutar el pipeline:

```bash
uv run python -m divisas_app.cli --update --input datos/divisas.csv --output resultados --ai-mode mock
```

Para utilizar el modo real:

```bash
uv run python -m divisas_app.cli --input datos/divisas.csv --output resultados --ai-mode real
```

Este último comando requiere una clave de API válida y puede generar costes asociados al proveedor.

## 7. Resultados generados

El pipeline genera los siguientes archivos en la carpeta `resultados/`:

| Archivo | Descripción |
|---|---|
| `divisas_limpias.csv` | Registros válidos sin duplicados |
| `registros_invalidos.csv` | Registros que no superan la validación |
| `duplicados.csv` | Registros duplicados detectados |
| `metricas_divisas.csv` | Estadísticas por par de divisas |
| `pipeline.log` | Registro de eventos de ejecución |
| `informe_ia.md` | Informe explicativo generado por el cliente de IA |

Las métricas incluyen el tipo de cambio medio, mínimo, máximo, número de registros y variación porcentual entre el primer y el último registro.

## 8. Integración de inteligencia artificial

La integración se encuentra en `src/divisas_app/ai_client.py`.

El cliente admite dos modos:

**Mock:** genera un informe local a partir de las métricas. No necesita conexión a OpenAI y permite realizar pruebas reproducibles.

**Real:** utiliza la API de OpenAI para generar un informe en español a partir de las métricas calculadas.

La IA se utiliza para explicar los resultados, no para predecir tipos de cambio futuros.

## 9. Pruebas

Para ejecutar todos los tests:

```bash
uv run pytest -v
```

El proyecto incluye 21 pruebas automatizadas que cubren la validación, el preprocesamiento, las métricas, la actualización de datos, el cliente de IA y el funcionamiento integrado del pipeline.

Las llamadas externas se simulan en los tests correspondientes para evitar depender de servicios externos durante las pruebas.

## 10. Arquitectura

El pipeline sigue este flujo:

1. Lectura del CSV y actualización opcional desde Frankfurter.
2. Validación de registros mediante Pydantic.
3. Eliminación de duplicados.
4. Cálculo de métricas estadísticas.
5. Generación del informe mediante el cliente de IA.
6. Exportación de CSV, informe Markdown y logs.

El sistema está dividido en módulos independientes para facilitar su mantenimiento y sus pruebas.

## 11. Limitaciones

- La disponibilidad de la actualización de datos depende de la API de Frankfurter.
- El modo real requiere credenciales y conexión a Internet.
- Los informes generados por IA pueden contener interpretaciones incorrectas.
- Las métricas históricas no garantizan comportamientos futuros.
- La conexión real con OpenAI está implementada, pero pendiente de validación con una petición auténtica.

## 12. Uso de herramientas de IA

El archivo `AI_USAGE.md` documenta cómo se ha utilizado ChatGPT durante el desarrollo del proyecto, así como las limitaciones y responsabilidades asociadas.