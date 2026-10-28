# Preparar el repositorio en GitHub

1. Crea un repositorio vacío en GitHub. No añadas README, `.gitignore` ni licencia desde la web, porque ya están en el código.
2. Extrae este ZIP o coloca los archivos en una carpeta local.
3. Desde esa carpeta, abre una terminal y ejecuta:

   ```powershell
   git init
   git add .
   git status
   git commit -m "Initial MiSistemaPortable project"
   git branch -M main
   git remote add origin https://github.com/TU-USUARIO/TU-REPOSITORIO.git
   git push -u origin main
   ```

4. En GitHub, abre **Actions** y comprueba que pasan `Tests` y `Build Windows Portable`.
5. Cuando el workflow termine, abre la ejecución de `Build Windows Portable` y descarga el artefacto `MiSistemaPortable-Windows-x64`.
6. Para publicar una versión, crea una Release en GitHub. Al publicarla, el workflow adjunta `MiSistemaPortable.exe` y `THIRD_PARTY_NOTICES.md` como assets.

Antes de ejecutar `git add`, revisa `git status`: `.gitignore` excluye el modelo GGUF, los runtimes descargados, los entornos de compilación, logs, datos personales y el EXE generado. No subas tokens, claves API, archivos `.session` ni credenciales.

Sustituye `TU-USUARIO` y `TU-REPOSITORIO` por los valores reales; no uses literalmente esa URL de ejemplo.
