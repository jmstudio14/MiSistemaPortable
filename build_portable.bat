@echo off
setlocal
cd /d "%~dp0"
echo ==================================================
echo MiSistemaPortable - Compilacion autocontenida
echo Este proceso descarga los componentes y genera un EXE unico.
echo La primera compilacion requiere conexion a Internet.
echo ==================================================
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\Build-Portable.ps1"
if errorlevel 1 (
  echo.
  echo ERROR: No se pudo generar el ejecutable. Lee el mensaje anterior.
  pause
  exit /b 1
)
echo.
echo EXE generado en dist\MiSistemaPortable.exe
echo Ya puedes copiar solo ese EXE a otra carpeta o unidad del mismo Windows.
pause
endlocal
