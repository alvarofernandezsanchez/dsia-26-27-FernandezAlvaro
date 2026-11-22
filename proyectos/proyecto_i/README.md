# Proyecto I — Pipeline de calidad de datos de ventas y divisas

## 1. Descripción

Proyecto desarrollado en Python para cargar, validar, limpiar y analizar datos mediante dos aplicaciones independientes:

- **Parte A — Ventas:** análisis de un dataset comercial, con validación de registros y cálculo de importes por región y producto.
- **Parte B — Divisas:** análisis de cotizaciones históricas, detección de registros incorrectos y duplicados, cálculo de estadísticas y actualización opcional mediante la API Frankfurter.

Se aplican conceptos de programación orientada a objetos (OOP), modularidad, estructuras de datos, gestión de excepciones, validación, documentación y pruebas automatizadas.

## 2. Tecnologías

- Python 3.12 o superior.
- pandas: procesamiento de datos de divisas.
- Pydantic: validación de cotizaciones.
- requests: conexión con la API Frankfurter.
- pytest: pruebas unitarias, parametrizadas y de integración.
- uv: gestión de dependencias y ejecución.
- GitHub Actions: integración continua.

## 3. Estructura del proyecto

```text
proyecto_i/
├── datos/
│   ├── ventas.csv
│   ├── ventas_prueba.csv
│   └── divisas.csv
├── src/
│   ├── ventas_app/
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   ├── validator.py
│   │   ├── metrics.py
│   │   └── cli.py
│   └── divisas_app/
│       ├── __init__.py
│       ├── contract.py
│       ├── loader.py
│       ├── validator.py
│       ├── metrics.py
│       ├── preprocess.py
│       ├── inference.py
│       ├── main.py
│       └── cli.py
├── tests/
├── pyproject.toml
├── uv.lock
└── README.md
```

Los módulos `preprocess.py` e `inference.py` se conservan por compatibilidad con el código y las pruebas anteriores. El procesamiento principal de divisas utiliza los nuevos módulos `loader.py`, `validator.py` y `metrics.py`.

## 4. Instalación

Desde la carpeta `proyectos/proyecto_i`:

```powershell
uv sync
```

Este comando crea o actualiza el entorno virtual e instala las dependencias del proyecto.

## 5. Parte A — Ventas

### Datos de entrada

El archivo `datos/ventas.csv` contiene las siguientes columnas:

| Campo | Descripción |
|---|---|
| `fecha` | Fecha de la venta |
| `region` | Región comercial |
| `producto` | Producto vendido |
| `unidades` | Número de unidades |
| `precio_unitario` | Precio de cada unidad |
| `cliente_id` | Identificador del cliente |

### Validación

Se comprueba que existan las columnas obligatorias, que los campos no estén vacíos, que las fechas tengan un formato válido, que las unidades sean enteros positivos y que los precios sean números no negativos.

Los errores se comunican mediante excepciones propias, indicando la fila y el campo afectado cuando corresponde.

### Métricas

Se calculan:

- Importe total de ventas.
- Importe vendido por región.
- Importe vendido por producto.
- Unidades totales vendidas.

El importe de cada venta se obtiene mediante:

**Importe = unidades × precio unitario**

Para los cálculos monetarios se utiliza `Decimal`.

### Ejecución

Para procesar el dataset original:

```powershell
uv run python -m ventas_app.cli --input datos/ventas.csv
```

El archivo original contiene al menos un registro con el campo `unidades` vacío. La aplicación lo detecta y muestra un error de validación.

Para comprobar el cálculo de métricas con datos válidos:

```powershell
uv run python -m ventas_app.cli --input datos/ventas_prueba.csv
```

El archivo de prueba contiene cuatro ventas válidas, con un importe total esperado de **738,50 €**.

## 6. Parte B — Divisas

### Fuente de datos

Se utilizan cotizaciones históricas de divisas. La actualización opcional se realiza mediante la API pública Frankfurter:

https://frankfurter.dev/

Cada registro contiene:

| Campo | Descripción |
|---|---|
| `date` | Fecha de cotización |
| `base` | Moneda de origen |
| `quote` | Moneda de destino |
| `rate` | Tipo de cambio |

### Validación y limpieza

El programa comprueba:

- Formato válido de las fechas.
- Códigos de moneda de tres letras mayúsculas.
- Monedas de origen y destino diferentes.
- Tipos de cambio positivos.
- Cotizaciones duplicadas para la misma fecha y par de monedas.

Los registros inválidos y duplicados se separan de los datos limpios.

### Métricas

Para cada par de monedas se calculan:

- Tipo de cambio medio.
- Tipo de cambio mínimo.
- Tipo de cambio máximo.
- Número de cotizaciones.
- Variación porcentual entre la primera y última cotización.

La variación se calcula mediante:

**Variación (%) = ((valor final − valor inicial) / valor inicial) × 100**

### Ejecución

Procesar el dataset existente:

```powershell
uv run python -m divisas_app.cli --input datos/divisas.csv --output resultados
```

Actualizar las cotizaciones desde Frankfurter y procesarlas:

```powershell
uv run python -m divisas_app.cli --update --input datos/divisas.csv --output resultados
```

La actualización requiere conexión a Internet y puede modificar el CSV de entrada.

### Archivos generados

La aplicación crea cuatro archivos en la carpeta de salida:

| Archivo | Contenido |
|---|---|
| `divisas_limpias.csv` | Registros válidos sin duplicados |
| `registros_invalidos.csv` | Registros que incumplen las reglas |
| `duplicados.csv` | Cotizaciones repetidas |
| `metricas_divisas.csv` | Estadísticas por par de monedas |

## 7. Organización del código

Ambas aplicaciones utilizan una estructura modular:

- `loader.py`: carga de archivos y comprobación de columnas.
- `validator.py`: validación de registros y reglas de calidad.
- `metrics.py`: cálculo de indicadores y estadísticas.
- `cli.py`: interfaz para ejecutar el programa desde la terminal.

En divisas, `contract.py` contiene el modelo Pydantic y las excepciones, mientras que `main.py` coordina el procesamiento y la exportación.

Esta separación permite probar y mantener cada componente de forma independiente.

## 8. Pruebas automatizadas

El proyecto incluye pruebas de:

- Carga y validación de datos.
- Registros incorrectos y casos límite.
- Detección de duplicados.
- Cálculo de métricas.
- Parametrización mediante `pytest.mark.parametrize`.
- Integración de las aplicaciones completas mediante sus CLI.
- Comportamiento de la actualización de divisas mediante pruebas con respuestas simuladas.

Para ejecutar todas las pruebas:

```powershell
uv run pytest -v
```

**Resultado verificado localmente: 41 tests superados.**

## 9. Integración continua

El repositorio dispone de un workflow en `.github/workflows/ci.yml` con un trabajo específico para el Proyecto I.

Está configurado para ejecutarse en GitHub Actions al subir cambios a `main` o `feature/proyecto-i`, así como en las solicitudes de incorporación de cambios (*pull requests*).

El trabajo instala Python, prepara el entorno con `uv` y ejecuta:

```powershell
uv run pytest -v
```

La ejecución correcta del workflow debe comprobarse en la pestaña **Actions** del repositorio.

## 10. Posibles mejoras

- Permitir descartar registros inválidos de ventas y continuar con los válidos.
- Exportar las métricas de ventas a CSV.
- Incorporar filtros de fechas y productos.
- Generar gráficos de evolución de cotizaciones.
- Ampliar los informes y formatos de exportación.

## 11. Uso de herramientas de IA

Se ha utilizado ChatGPT como herramienta de apoyo para revisar la organización del código, preparar casos de prueba y mejorar la documentación. Las modificaciones se han comprobado mediante ejecuciones locales y pruebas automatizadas.