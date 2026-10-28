$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$BuildDir = Join-Path $Root '.build-tools'
$VenvDir = Join-Path $Root '.build-venv'
$ModelDir = Join-Path $Root 'models'
$ModelPath = Join-Path $ModelDir 'qwen2.5-0.5b-instruct-q4_k_m.gguf'
$VendorDir = Join-Path $Root 'vendor'
$NodeDir = Join-Path $VendorDir 'node'
$DcDir = Join-Path $VendorDir 'desktop-commander'
$PythonExe = Join-Path $VenvDir 'Scripts\python.exe'

function Write-Step([string]$Message) {
  Write-Host "`n[MiSistemaPortable] $Message" -ForegroundColor Cyan
}
function Download-File([string]$Url, [string]$Destination) {
  if (Test-Path $Destination) { Remove-Item $Destination -Force }
  Write-Host "Descargando: $Url"
  Invoke-WebRequest -Uri $Url -OutFile $Destination -UseBasicParsing
  if (!(Test-Path $Destination) -or (Get-Item $Destination).Length -lt 100000) {
    throw "Descarga incompleta: $Destination"
  }
}

function Invoke-Native([string]$FilePath, [string[]]$Arguments, [string]$Label) {
  # Windows PowerShell 5.1 may promote native stderr output to terminating errors.
  $previousPreference = $ErrorActionPreference
  $ErrorActionPreference = 'Continue'
  try {
    & $FilePath @Arguments
    $nativeExitCode = $LASTEXITCODE
  } finally {
    $ErrorActionPreference = $previousPreference
  }
  if ($nativeExitCode -ne 0) {
    throw "$Label falló con código $nativeExitCode. Revisa el registro de compilación."
  }
}

New-Item -ItemType Directory -Force -Path $BuildDir, $ModelDir, $VendorDir | Out-Null

# 1. Model weights. No login or API key is required for this public model.
if (!(Test-Path $ModelPath) -or (Get-Item $ModelPath).Length -lt 250000000) {
  Write-Step 'Descargando modelo GGUF oficial de Qwen…'
  $tempModel = "$ModelPath.download"
  Download-File 'https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf?download=true' $tempModel
  $size = (Get-Item $tempModel).Length
  if ($size -lt 250000000 -or $size -gt 524288000) {
    Remove-Item $tempModel -Force -ErrorAction SilentlyContinue
    throw "Tamaño inesperado del modelo: $size bytes. No se usará un archivo incompleto o distinto."
  }
  Move-Item $tempModel $ModelPath -Force
} else {
  $size = (Get-Item $ModelPath).Length
  if ($size -gt 524288000) { throw 'El archivo GGUF existente supera el límite validado de 500 MiB.' }
  Write-Step 'Modelo GGUF ya descargado; se reutiliza.'
}

# 2. Download uv as a build-only bootstrapper. It installs a private Python runtime
# into the build environment; neither uv nor Python is required by the finished EXE.
$UvZip = Join-Path $BuildDir 'uv-win-x64.zip'
$UvExtract = Join-Path $BuildDir 'uv-extracted'
$UvExe = Join-Path $BuildDir 'uv.exe'
if (!(Test-Path $UvExe)) {
  Write-Step 'Preparando herramientas de compilación (sin instalación manual)…'
  Download-File 'https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip' $UvZip
  if (Test-Path $UvExtract) { Remove-Item $UvExtract -Recurse -Force }
  Expand-Archive -Path $UvZip -DestinationPath $UvExtract -Force
  $foundUv = Get-ChildItem -Path $UvExtract -Filter 'uv.exe' -Recurse | Select-Object -First 1
  if (!$foundUv) { throw 'No se encontró uv.exe dentro del archivo oficial descargado.' }
  Copy-Item $foundUv.FullName $UvExe -Force
}

$env:UV_CACHE_DIR = Join-Path $BuildDir 'uv-cache'
Invoke-Native $UvExe @('python', 'install', '3.11') 'Instalación privada de Python'
if (!(Test-Path $PythonExe)) {
  Invoke-Native $UvExe @('venv', '--python', '3.11', $VenvDir) 'Creación del entorno de compilación'
}

Write-Step 'Instalando dependencias en el entorno temporal de compilación…'
try {
  Invoke-Native $UvExe @('pip', 'install', '--python', $PythonExe, '--index-strategy', 'unsafe-best-match', '--extra-index-url', 'https://abetlen.github.io/llama-cpp-python/whl/cpu', '-r', (Join-Path $Root 'requirements-build.txt')) 'Instalación de dependencias'
} catch { throw 'Falló la instalación automática de dependencias. No se ha generado un EXE incompleto. ' + $_.Exception.Message }

# 3. Download a Node LTS version that satisfies the current Desktop Commander package.
# It is used only during build to install the precompiled npm package. Only node.exe
# and the package runtime are put into the one-file application.
$NodeFull = Join-Path $BuildDir 'node-full'
$NodeZip = Join-Path $BuildDir 'node-win-x64.zip'
if (!(Test-Path (Join-Path $NodeDir 'node.exe')) -or !(Test-Path (Join-Path $DcDir 'node_modules\@wonderwhy-er\desktop-commander\dist\index.js'))) {
  Write-Step 'Descargando Node.js LTS portable y Desktop Commander…'
  $index = Invoke-RestMethod -Uri 'https://nodejs.org/dist/index.json'
  $lts = $index | Where-Object { $_.lts -and $_.version -match '^v(\d+)' -and [int]$Matches[1] -ge 22 } | Select-Object -First 1
  if (!$lts) { throw 'No se encontró una versión LTS de Node.js compatible (>=22).' }
  $nodeVersion = $lts.version
  $nodeZipUrl = "https://nodejs.org/dist/$nodeVersion/node-$nodeVersion-win-x64.zip"
  Download-File $nodeZipUrl $NodeZip
  if (Test-Path $NodeFull) { Remove-Item $NodeFull -Recurse -Force }
  Expand-Archive -Path $NodeZip -DestinationPath $NodeFull -Force
  $NodeExeFull = Get-ChildItem -Path $NodeFull -Filter 'node.exe' -Recurse | Select-Object -First 1
  $NpmCmd = Get-ChildItem -Path $NodeFull -Filter 'npm.cmd' -Recurse | Select-Object -First 1
  if (!$NodeExeFull -or !$NpmCmd) { throw 'El paquete de Node.js no contiene node.exe y npm.cmd.' }
  New-Item -ItemType Directory -Force -Path $NodeDir, $DcDir | Out-Null
  Copy-Item $NodeExeFull.FullName (Join-Path $NodeDir 'node.exe') -Force
  # Desktop Commander ships compiled dist files on npm. Ignore install scripts to avoid
  # setup side-effects/telemetry at build time; telemetry is disabled in the runtime config.
  $env:npm_config_update_notifier = 'false'
  Invoke-Native $NpmCmd.FullName @('install', '--prefix', $DcDir, '--omit=dev', '--ignore-scripts', '--no-audit', '--no-fund', '@wonderwhy-er/desktop-commander@0.3.1') 'Instalación de Desktop Commander'
  if (!(Test-Path (Join-Path $DcDir 'node_modules\@wonderwhy-er\desktop-commander\dist\index.js'))) {
    throw 'El paquete npm no contiene el punto de entrada esperado dist/index.js.'
  }
}

# 4. Validate the files before asking PyInstaller to create a one-file executable.
if (!(Test-Path $ModelPath)) { throw 'Falta el modelo GGUF.' }
if (!(Test-Path (Join-Path $NodeDir 'node.exe'))) { throw 'Falta el runtime de Node.js.' }
if (!(Test-Path (Join-Path $DcDir 'node_modules\@wonderwhy-er\desktop-commander\dist\index.js'))) { throw 'Falta Desktop Commander.' }

Write-Step 'Compilando ejecutable único con Python, modelo, dependencias y Node/MCP embebidos…'
Push-Location $Root
try {
  Invoke-Native $PythonExe @('-m', 'PyInstaller', '--noconfirm', '--clean', (Join-Path $Root 'MiSistemaPortable.spec')) 'Compilación PyInstaller'
} finally {
  Pop-Location
}

$ExePath = Join-Path $Root 'dist\MiSistemaPortable.exe'
if (!(Test-Path $ExePath)) { throw 'La compilación terminó sin producir MiSistemaPortable.exe.' }
$exeMB = [math]::Round((Get-Item $ExePath).Length / 1MB, 1)
Write-Step "ÉXITO: $ExePath ($exeMB MiB)"
Write-Host 'El EXE incluye Python, llama.cpp, el GGUF, dependencias Python, node.exe y Desktop Commander.' -ForegroundColor Green
Write-Host 'El ejecutable final no necesita instalar Python, Node.js, pip ni Ollama.' -ForegroundColor Green
