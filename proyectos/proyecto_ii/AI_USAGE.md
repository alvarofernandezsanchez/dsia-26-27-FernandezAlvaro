# AI_USAGE — Proyecto II

## 1. Herramientas de IA utilizadas

Durante el desarrollo del Proyecto II se ha utilizado **ChatGPT (OpenAI)** como herramienta de apoyo para la programación, la explicación de conceptos, la depuración de errores, la preparación de pruebas y la elaboración de documentación.

Además, el proyecto incorpora un cliente de inteligencia artificial que permite generar informes explicativos a partir de las métricas estadísticas calculadas sobre los tipos de cambio.

Para esta funcionalidad se han contemplado dos proveedores:

- **NVIDIA Nemotron:** proveedor utilizado y validado mediante una petición real a su API.
- **OpenAI:** proveedor alternativo implementado y comprobado mediante pruebas automatizadas con respuestas simuladas.

## 2. Uso de IA durante el desarrollo

ChatGPT se ha utilizado como apoyo para:

- Diseñar la estructura del pipeline y su integración con servicios externos.
- Implementar el sistema de logs y la configuración mediante variables de entorno.
- Desarrollar el cliente de IA con los modos `mock` y `real`.
- Incorporar la selección entre los proveedores NVIDIA y OpenAI.
- Preparar pruebas unitarias y de integración mediante `pytest`.
- Identificar y corregir errores durante la ejecución.
- Interpretar los resultados obtenidos en las pruebas.
- Elaborar y actualizar la documentación técnica del proyecto.

El código se ha integrado y comprobado localmente mediante ejecuciones del pipeline y pruebas automatizadas.

La utilización de ChatGPT ha servido como apoyo al desarrollo. Las funcionalidades implementadas se han contrastado mediante pruebas y ejecuciones del programa.

## 3. Integración de IA en el proyecto

El archivo `src/divisas_app/ai_client.py` implementa dos modos de funcionamiento.

### Modo mock

Genera un informe determinista a partir de las métricas calculadas, sin realizar peticiones a servicios externos.

Este modo permite:

- Ejecutar el pipeline sin credenciales.
- Obtener resultados reproducibles.
- Realizar pruebas automatizadas sin depender de una API externa.

### Modo real

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

Se han desarrollado pruebas automatizadas para comprobar el funcionamiento del pipeline y del cliente de inteligencia artificial.

La batería de pruebas incluye:

- Comprobaciones del modo `mock`.
- Simulación de respuestas del proveedor OpenAI.
- Simulación de respuestas del proveedor NVIDIA.
- Comprobación de errores relacionados con la ausencia de credenciales.
- Pruebas del funcionamiento integrado del pipeline.

Durante la revisión del proyecto se ejecutaron **27 pruebas automatizadas**, todas superadas.

### Validación real con NVIDIA

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

- Los modelos pueden generar interpretaciones incorrectas o información que no esté respaldada por los datos.
- Las cifras presentadas en los informes pueden aparecer redondeadas.
- La comprobación manual realizada sobre el informe de NVIDIA no abarca todos los valores generados.
- El acceso a las APIs externas depende de su disponibilidad, las credenciales y los límites de uso.
- Las respuestas de un modelo pueden variar entre ejecuciones.
- Los resultados históricos de divisas no permiten garantizar comportamientos futuros.

Los informes generados no constituyen asesoramiento financiero.

La responsabilidad de revisar el código, comprobar los resultados y validar el funcionamiento del proyecto corresponde al desarrollador.

## 6. Conclusión

La inteligencia artificial se ha utilizado en dos ámbitos diferenciados: como herramienta de apoyo durante el desarrollo y como servicio externo integrado en el funcionamiento del programa.

El pipeline realiza la lectura, validación, limpieza y análisis estadístico de los datos mediante código Python.

Posteriormente, el cliente de IA utiliza las métricas calculadas para elaborar un informe explicativo.

La implementación permite trabajar sin conexión a un proveedor de IA mediante el modo `mock` y generar informes mediante NVIDIA u OpenAI en el modo `real`.

La conexión real con NVIDIA Nemotron se ha comprobado satisfactoriamente, mientras que el funcionamiento del cliente y del pipeline se ha verificado mediante pruebas automatizadas.