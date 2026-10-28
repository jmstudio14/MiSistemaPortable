# Contribuir

1. Trabaja en una rama separada.
2. Mantén el modelo y los runtimes de terceros fuera del control de versiones; el build script los obtiene durante la compilación.
3. Ejecuta las pruebas antes de abrir un pull request:

   ```powershell
   python -m unittest discover -s tests -v
   ```

4. Si cambias permisos o acciones, añade tests positivos y negativos a `tests/`.
5. No añadas ejecución de shell arbitraria ni acciones destructivas sin diseño de seguridad y aprobación humana.
6. No incluyas credenciales, ficheros de sesión de Telegram, datos personales ni logs con rutas privadas.

Los cambios de dependencias deben quedar fijados en los ficheros de requisitos y revisarse junto con `THIRD_PARTY_NOTICES.md`.
