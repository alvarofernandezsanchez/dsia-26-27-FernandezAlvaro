# AI_USAGE — Proyecto II

## 1. Herramientas de IA utilizadas

Durante el desarrollo del Proyecto II se ha utilizado ChatGPT (OpenAI) como herramienta de apoyo para la programación, la explicación de conceptos, la depuración de errores y la preparación de pruebas.

Además, el proyecto incorpora un cliente de IA que permite generar informes a partir de las métricas calculadas sobre los tipos de cambio.

## 2. Uso de IA durante el desarrollo

ChatGPT se ha utilizado como apoyo para:

- Diseñar la estructura del pipeline y su integración con un servicio externo.
- Implementar el sistema de logs y la configuración mediante variables de entorno.
- Desarrollar el cliente de IA con los modos `mock` y `real`.
- Preparar tests unitarios y de integración con `pytest`.
- Identificar y corregir errores durante la ejecución.
- Elaborar documentación técnica.

El código se ha integrado y comprobado localmente mediante ejecuciones del pipeline y pruebas automatizadas.

## 3. Integración de IA en el proyecto

El archivo `ai_client.py` implementa dos modos de funcionamiento:

**Modo mock:** genera un informe determinista a partir de las métricas, sin realizar peticiones a servicios externos. Permite probar el funcionamiento del pipeline sin necesidad de credenciales.

**Modo real:** utiliza la API de OpenAI para solicitar un informe en español a partir de las métricas de divisas.

El modo de funcionamiento se configura mediante `AI_MODE` en el archivo `.env` o mediante el argumento `--ai-mode` del CLI.

## 4. Validación y limitaciones

Se han desarrollado pruebas automatizadas para comprobar el funcionamiento del cliente de IA, incluyendo una simulación de la respuesta de OpenAI mediante `unittest.mock`.

También se ha incorporado un test de integración que comprueba el funcionamiento del pipeline completo.

Los informes generados no constituyen asesoramiento financiero. El modelo de IA puede producir interpretaciones incorrectas, por lo que sus resultados deben revisarse antes de utilizarlos.

El modo `mock` se ha validado mediante pruebas automatizadas y ejecuciones completas del pipeline. La integración con OpenAI está implementada y se ha probado mediante respuestas simuladas, pero todavía no se ha validado mediante una petición real a la API.