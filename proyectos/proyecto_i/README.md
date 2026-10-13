# Proyecto I — Pipeline de calidad de datos de divisas

## 1. Descripción

Aplicación desarrollada en Python para descargar, validar, limpiar y analizar tipos de cambio de distintas divisas respecto al euro (EUR).

El proyecto utiliza datos históricos de la API pública **Frankfurter** y permite actualizar automáticamente el dataset, detectar registros incorrectos o duplicados y generar informes estadísticos.

Se han aplicado conceptos de programación orientada a objetos, modularidad, validación de datos, gestión de excepciones y pruebas automáticas.

## 2. Tecnologías utilizadas

- Python
- pandas: procesamiento y análisis de datos.
- Pydantic: validación de registros.
- requests: conexión con la API.
- pytest: pruebas automáticas.
- uv: gestión de dependencias y entorno de ejecución.

## 3. Fuente de datos

Los datos proceden de la API pública Frankfurter:

https://frankfurter.dev/

Cada registro contiene cuatro campos:

| Campo | Descripción |
|---|---|
| `date` | Fecha de la cotización |
| `base` | Moneda de origen |
| `quote` | Moneda de destino |
| `rate` | Tipo de cambio |

El dataset inicial contiene cotizaciones históricas desde 2023 y puede actualizarse mediante la API.

## 4. Estructura del proyecto

```text
proyecto_i/
├── datos/
│   └── divisas.csv
├── resultados/
├── src/
│   └── divisas_app/
│       ├── __init__.py
│       ├── contract.py
│       ├── preprocess.py
│       ├── inference.py
│       ├── main.py
│       └── cli.py
├── tests/
│   ├── test_contract.py
│   ├── test_preprocess.py
│   ├── test_inference.py
│   └── test_api.py
├── pyproject.toml
├── uv.lock
└── README.md
```

## 5. Instalación

Es necesario tener instalados Python y `uv`.

Desde la carpeta `proyecto_i`, ejecutar:

```bash
uv sync
```

Este comando prepara el entorno e instala las dependencias definidas en el proyecto.

## 6. Ejecución

### Procesar el dataset existente

```bash
uv run python -m divisas_app.cli --input datos/divisas.csv --output resultados
```

### Actualizar los datos desde Frankfurter y procesarlos

```bash
uv run python -m divisas_app.cli --update --input datos/divisas.csv --output resultados
```

También es posible utilizar los valores predeterminados:

```bash
uv run python -m divisas_app.cli --update
```

## 7. Validación y limpieza

El programa comprueba:

- Que las fechas tengan un formato válido.
- Que los códigos de divisas contengan tres letras mayúsculas.
- Que las monedas de origen y destino sean diferentes.
- Que los tipos de cambio sean positivos.
- Que no existan cotizaciones duplicadas para una misma fecha y par de monedas.

Los registros incorrectos y duplicados se separan de los datos limpios.

## 8. Métricas calculadas

Para cada par de divisas se calculan:

- Tipo de cambio medio.
- Tipo de cambio mínimo.
- Tipo de cambio máximo.
- Número de registros.
- Variación porcentual entre la primera y última cotización.

La variación porcentual se calcula mediante:

**Variación (%) = ((valor final - valor inicial) / valor inicial) × 100**

## 9. Archivos generados

La aplicación crea cuatro archivos CSV en la carpeta de resultados:

| Archivo | Contenido |
|---|---|
| `divisas_limpias.csv` | Registros válidos sin duplicados |
| `registros_invalidos.csv` | Registros que incumplen las reglas |
| `duplicados.csv` | Cotizaciones repetidas |
| `metricas_divisas.csv` | Informe estadístico por divisa |

## 10. Pruebas automáticas

El proyecto utiliza pytest para verificar la validación de datos, la detección de duplicados, los cálculos estadísticos y la actualización mediante la API.

Para ejecutar los tests:

```bash
uv run pytest -v
```

Se han implementado 15 pruebas automáticas, incluyendo simulaciones de respuestas de Frankfurter que no requieren conexión real a Internet.

## 11. Organización del código

- `contract.py`: modelos de datos, reglas de validación y excepciones personalizadas.
- `preprocess.py`: carga, validación, limpieza y actualización del dataset.
- `inference.py`: cálculo de estadísticas y variaciones.
- `main.py`: coordinación del pipeline y exportación de resultados.
- `cli.py`: interfaz de línea de comandos.
- `tests/`: pruebas automáticas de los componentes.

## 12. Posibles mejoras futuras

- Incorporar nuevas monedas.
- Permitir seleccionar intervalos de fechas desde la CLI.
- Generar gráficos de evolución de cotizaciones.
- Exportar informes en otros formatos.
