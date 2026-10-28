@echo off
setlocal
cd /d "%~dp0"
if exist "dist\MiSistemaPortable.exe" (
  start "" "%~dp0dist\MiSistemaPortable.exe"
) else (
  echo Todavia no se ha generado el ejecutable autocontenido.
  echo Haz doble clic en build_portable.bat. Ese proceso prepara las dependencias y compila el EXE.
  pause
)
endlocal
