# Seguridad

## Versión actual

MiSistemaPortable es un prototipo. Las salidas de un modelo de lenguaje pueden ser incorrectas o maliciosas, y no deben considerarse instrucciones de confianza.

En esta versión:

- No se evalúa ni ejecuta código generado por el modelo.
- No se ejecutan cadenas arbitrarias de PowerShell o CMD.
- Las acciones que modifican o eliminan archivos y las llamadas MCP genéricas están bloqueadas.
- El módulo de Telegram no conecta ni lee credenciales automáticamente.

## Uso seguro

Prueba el programa con carpetas de prueba y datos prescindibles. No lo ejecutes con privilegios de administrador. Antes de habilitar nuevas herramientas, crea una política de permisos por carpeta, confirma los parámetros exactos antes de modificar archivos y prueba que las acciones no autorizadas quedan bloqueadas.

## Informar de una vulnerabilidad

No publiques detalles explotables de una vulnerabilidad en un issue público. Si GitHub tiene habilitado el aviso privado de vulnerabilidades para el repositorio, úsalo; si no, contacta de forma privada con el propietario del repositorio antes de divulgarla.
