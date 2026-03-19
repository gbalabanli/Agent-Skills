@echo off
setlocal EnableExtensions

set "PORT=8765"
set "MODE=normal"

:parse_args
if "%~1"=="" goto args_done
if /I "%~1"=="--help" goto help
if /I "%~1"=="--demo" (
  set "MODE=demo"
  shift
  goto parse_args
)
if /I "%~1"=="--port" (
  if "%~2"=="" (
    echo Missing value for --port
    exit /b 1
  )
  set "PORT=%~2"
  shift
  shift
  goto parse_args
)

echo Unknown argument: %~1
echo Use --help for usage.
exit /b 1

:args_done
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..\..\..") do set "REPO_ROOT=%%~fI"

set "TOOL_URL=http://127.0.0.1:%PORT%/designing/design-to-code-annotator/assets/annotation-tool/index.html"
if /I "%MODE%"=="demo" (
  set "TOOL_URL=%TOOL_URL%?demo=1"
)

where python >nul 2>nul
if errorlevel 1 (
  echo Python is not available on PATH. Install Python 3 and try again.
  exit /b 1
)

echo Starting annotation tool server on port %PORT%
echo Opening %TOOL_URL%
echo Press Ctrl+C in this window to stop the server.

start "" "%TOOL_URL%"
pushd "%REPO_ROOT%"
python -m http.server %PORT%
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%

:help
echo Usage: %~nx0 [--demo] [--port PORT]
echo.
echo   --demo       Open tool with demo data preloaded.
echo   --port PORT  Local server port ^(default: 8765^).
echo.
echo This script should stay next to index.html in assets\annotation-tool.
exit /b 0
