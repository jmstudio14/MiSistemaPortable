# Arquitectura

## Flujo de una orden

1. `app_gui.py` recoge la orden y la envía al `TaskRunner` sin bloquear Tkinter.
2. `TaskRunner` reconoce unas pocas órdenes de consulta deterministas; si no encajan, llama a `SlmEngine`.
3. `SlmEngine` genera una intención JSON usando `llama-cpp-python` y el modelo GGUF local.
4. `json_parser.py` intenta extraer un objeto JSON, incluso si el modelo añade texto alrededor.
5. `guardrails.py` valida el nombre de acción y el tipo de parámetros mediante una lista permitida.
6. `TaskRunner` ejecuta solo las acciones implementadas en esta versión.
7. La respuesta vuelve a la cola que consume la interfaz.

## Rutas en modo desarrollo y en modo EXE

`core/paths.py` distingue entre:

- `SOURCE_ROOT`: raíz del código en desarrollo.
- `RESOURCE_ROOT`: raíz del paquete; en PyInstaller `--onefile` apunta a `_MEIPASS`, donde se extraen recursos embebidos.
- `APP_ROOT`: ubicación del ejecutable durante la ejecución empaquetada.
- `DATA_ROOT`: datos persistentes y configuración runtime local junto al EXE.

No se debe escribir información persistente dentro de `_MEIPASS`: es una ubicación temporal.

## Límites de seguridad actuales

- No se ejecutan comandos de shell generados por el SLM.
- Las acciones de escritura, borrado y ejecución arbitraria están denegadas por defecto.
- La interfaz MCP solo enumera herramientas; no expone aún el mecanismo genérico de llamada a herramientas al modelo.
- Las rutas elegidas por el usuario todavía necesitan una UX de permisos más estricta antes de ampliar acciones.

Antes de permitir acciones de escritura, añade vista previa, confirmación humana vinculada a parámetros concretos, límites de carpeta y tests de seguridad.
