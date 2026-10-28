# MiSistemaPortable

Asistente de automatización local para Windows, con un modelo GGUF ejecutado dentro del proceso Python y Desktop Commander mediante MCP sobre stdio.

> **Estado: prototipo funcional en desarrollo.** La interfaz, inferencia local, listado/búsqueda de archivos de solo lectura y descubrimiento de herramientas MCP están preparados. Las acciones destructivas, la ejecución arbitraria de comandos y las llamadas MCP arbitrarias permanecen bloqueadas. La automatización de Telegram aún es un módulo de comprobación, no un descargador completo.

## Objetivo de distribución

El proyecto puede compilarse como un único archivo `dist\MiSistemaPortable.exe`. El ejecutable se empaqueta con Python, Tkinter, `llama-cpp-python` y sus bibliotecas, el modelo Qwen GGUF, las dependencias Python, el runtime `node.exe` y Desktop Commander.

En el equipo de destino **no hace falta instalar Python, Node.js, pip, npm, Visual Studio ni Ollama**. El proceso de construcción descarga automáticamente los componentes necesarios.

## Compilar en Windows

Requisitos para crear el EXE: Windows x64, conexión a Internet durante la primera compilación y espacio libre de varios GB para los archivos temporales. No se requieren instalaciones manuales de runtimes.

1. Descarga o clona este repositorio.
2. En Windows, ejecuta `build_portable.bat`.
3. El script obtiene automáticamente una versión privada de Python, las dependencias, el modelo oficial GGUF, Node.js y Desktop Commander, y ejecuta PyInstaller.
4. Al terminar correctamente, el ejecutable estará en `dist\MiSistemaPortable.exe`.
5. Copia ese único EXE a otra carpeta o unidad del **mismo Windows** y ábrelo.

La primera compilación requiere Internet. El ejecutable resultante no necesita conectarse a una API de IA ni a un servicio de inferencia para cargar el modelo. Las funciones de Telegram, cuando se implementen y activen, necesitarán comunicación con Telegram.

### GitHub Actions

- `Tests` ejecuta las pruebas unitarias en cada push y pull request.
- `Build Windows Portable` compila el EXE en Windows cuando se hace push a `main`/`master`, al ejecutar manualmente el workflow o al publicar una release.
- Las ejecuciones del workflow suben el EXE como artefacto descargable. Al publicar una release, el EXE y los avisos de terceros también se adjuntan a esa release.

Consulta [docs/BUILD_FROM_SOURCE.md](docs/BUILD_FROM_SOURCE.md) y [docs/GITHUB.md](docs/GITHUB.md).

## Contenido del repositorio

```text
MiSistemaPortable/
├── .github/workflows/       # Pruebas y compilación automática en GitHub
├── config/settings.yaml     # Configuración por defecto
├── core/
│   ├── guardrails.py        # Política de acciones permitidas
│   ├── json_parser.py       # Extracción tolerante de JSON
│   ├── mcp_manager.py       # Cliente MCP para Desktop Commander
│   ├── paths.py             # Rutas portables y datos persistentes
│   ├── slm_engine.py        # Motor llama-cpp-python y prompt del SLM
│   └── task_runner.py       # Cola de tareas en segundo plano
├── docs/                    # Arquitectura, construcción y publicación
├── models/                  # Carpeta vacía; el GGUF se descarga al compilar
├── scripts/Build-Portable.ps1
├── tests/                   # Pruebas unitarias sin servicios externos
├── app_gui.py               # Interfaz Tkinter
├── descargar_telegram.py    # Comprobación del módulo opcional de Telegram
├── ordenes.yaml             # Macros declarativas
├── MiSistemaPortable.spec   # Configuración de PyInstaller
├── requirements.txt         # Dependencias de ejecución fijadas
├── requirements-build.txt   # Dependencias del proceso de compilación
├── build_portable.bat       # Compila el EXE sin instalaciones manuales
└── run.bat                  # Abre el EXE compilado si existe
```

## Qué hace esta versión

- Ejecuta `Qwen2.5-0.5B-Instruct` en formato GGUF a través de `llama-cpp-python`, en el mismo proceso Python.
- Mantiene la interfaz Tkinter receptiva: la inferencia y las operaciones de I/O se hacen en un hilo de trabajo.
- Puede enumerar archivos de una carpeta y buscar coincidencias por nombre en modo de solo lectura.
- Puede iniciar Desktop Commander como proceso hijo local por MCP stdio y enumerar las herramientas que anuncia.
- Extrae objetos JSON de respuestas del modelo y valida la acción mediante una lista permitida independiente.
- Mantiene la organización de archivos, el borrado, las llamadas MCP arbitrarias y los comandos arbitrarios deshabilitados.
- No incluye claves API, credenciales ni sesiones de Telegram.

## Pruebas de desarrollo

Con Python 3.11 o posterior instalado **solo para desarrollo**, desde la raíz del repositorio:

```powershell
python -m unittest discover -s tests -v
```

Las pruebas unitarias actuales usan la biblioteca estándar de Python. No descargan modelos ni se conectan a MCP.

## Portabilidad y tamaño

El `.exe` de un solo archivo extrae recursos temporalmente al iniciarse, de modo que el primer arranque puede ser más lento y necesita espacio temporal. Los datos mutables se guardan en `data\` junto al EXE; el modelo y los runtimes se leen de los recursos embebidos.

El EXE es para Windows x64. La portabilidad objetivo es entre carpetas y unidades del mismo equipo, no una garantía de compatibilidad con cualquier versión de Windows o cualquier otro equipo. Hay que probarlo en el Windows de destino antes de distribuirlo.

## Seguridad

El modelo no es una frontera de seguridad. Sus salidas se tratan como datos no confiables. No se evalúa texto generado como PowerShell, CMD o código Python. Revisa [SECURITY.md](SECURITY.md) antes de habilitar nuevas herramientas.

## Modelo y dependencias de terceros

El archivo GGUF (casi 500 MB) y `node_modules` **no se almacenan en GitHub**. El proceso de construcción descarga versiones definidas en `scripts/Build-Portable.ps1` y dependencias fijadas en `requirements*.txt`. Conserva [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) al redistribuir compilaciones y revisa las licencias vigentes de todos los componentes.

Este repositorio no incluye todavía una licencia propia de proyecto. Antes de hacerlo público o redistribuir código, elige explícitamente una licencia para el código de este proyecto.
