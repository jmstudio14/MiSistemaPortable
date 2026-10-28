# Construcción desde el código fuente

## Equipo de destino

El EXE está pensado para Windows x64. No necesita que el equipo de destino tenga Python, Node.js, npm, Ollama ni un compilador C++ instalados.

## Requisitos de la primera compilación

- Windows x64.
- Acceso a Internet para descargar el modelo Qwen, el bootstrapper de `uv`, Python privado, dependencias Python, Node.js y Desktop Commander.
- Varios GB libres para descargas, cachés y archivos temporales del proceso de empaquetado.

## Pasos

1. Clona o descarga el repositorio.
2. Ejecuta `build_portable.bat`, o abre PowerShell y ejecuta `.\scripts\Build-Portable.ps1` desde la raíz.
3. Espera a que el proceso compruebe los recursos y compile el EXE.
4. Comprueba que exista `dist\MiSistemaPortable.exe`.
5. Prueba el EXE en el Windows de destino, preferiblemente en una carpeta temporal que no contenga documentos importantes.

El script fija las dependencias Python mediante `requirements.txt` y `requirements-build.txt`, valida el tamaño del modelo descargado y fija la versión npm de Desktop Commander. La versión de Node.js se elige dinámicamente entre las versiones LTS disponibles que cumplen la versión mínima requerida por Desktop Commander; para builds reproducibles estrictos, fija también una versión exacta de Node.js y conserva un inventario de hashes.

## Errores frecuentes

- **Descarga incompleta:** comprueba conexión, proxy/firewall y espacio libre; vuelve a ejecutar el script. El modelo ya completo se reutiliza.
- **Falta de espacio temporal:** libera varios GB y vuelve a ejecutar.
- **El EXE no arranca en otro equipo:** valida Windows x64 y prueba desde una carpeta local con permisos de escritura; revisa el antivirus y las dependencias del sistema operativo.
- **La lista MCP falla:** confirma que el paquete de Desktop Commander se descargó correctamente y que el runtime incluido es Node.js x64.

No distribuyas el EXE hasta probarlo en una instalación limpia de Windows sin runtimes de desarrollo.
