@echo off
setlocal EnableExtensions

title Race Engineer Analytics

REM ============================================================
REM Race Engineer Analytics - Dashboard Launcher
REM ============================================================

set "PROJECT_DIR=D:\Analysis"
set "DASHBOARD=scripts\dashboard.py"
set "PYTHON_EXE="

cd /d "%PROJECT_DIR%"

echo ==========================================
echo Race Engineer Analytics
echo ==========================================
echo Project:
echo   %PROJECT_DIR%
echo.

REM ------------------------------------------------------------
REM 1. Look for project virtual environment
REM ------------------------------------------------------------

if exist "%PROJECT_DIR%\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%PROJECT_DIR%\.venv\Scripts\python.exe"
)

REM ------------------------------------------------------------
REM 2. Look for virtual environment in user folder
REM ------------------------------------------------------------

if not defined PYTHON_EXE (
    if exist "C:\Users\CAlbe\.venv\Scripts\python.exe" (
        set "PYTHON_EXE=C:\Users\CAlbe\.venv\Scripts\python.exe"
    )
)

REM ------------------------------------------------------------
REM 3. Look for Python installed in PATH
REM ------------------------------------------------------------

if not defined PYTHON_EXE (
    for /f "delims=" %%I in ('where python 2^>nul') do (
        if not defined PYTHON_EXE (
            set "PYTHON_EXE=%%I"
        )
    )
)

REM ------------------------------------------------------------
REM Python not found
REM ------------------------------------------------------------

if not defined PYTHON_EXE (
    echo ERROR: No Python installation was found.
    echo.
    echo Checked:
    echo   %PROJECT_DIR%\.venv\Scripts\python.exe
    echo   C:\Users\CAlbe\.venv\Scripts\python.exe
    echo   Python available in PATH
    echo.
    pause
    exit /b 1
)

REM ------------------------------------------------------------
REM Check dashboard file
REM ------------------------------------------------------------

if not exist "%PROJECT_DIR%\%DASHBOARD%" (
    echo ERROR: Dashboard file not found.
    echo.
    echo Expected:
    echo   %PROJECT_DIR%\%DASHBOARD%
    echo.
    pause
    exit /b 1
)

echo Python selected:
echo   %PYTHON_EXE%
echo.

echo Dashboard:
echo   %PROJECT_DIR%\%DASHBOARD%
echo.

REM ------------------------------------------------------------
REM Check required Python packages
REM ------------------------------------------------------------

"%PYTHON_EXE%" -c "import streamlit, pandas, plotly" >nul 2>&1

if errorlevel 1 (
    echo ERROR: Required Python packages are missing.
    echo.
    echo Install them with:
    echo.
    echo   "%PYTHON_EXE%" -m pip install streamlit plotly pandas
    echo.
    pause
    exit /b 1
)

REM ------------------------------------------------------------
REM Start Streamlit dashboard
REM ------------------------------------------------------------

echo ==========================================
echo Starting Race Engineer Analytics...
echo ==========================================
echo.
echo Dashboard URL:
echo   http://localhost:8501
echo.
echo Press CTRL+C to stop the dashboard.
echo.

"%PYTHON_EXE%" -m streamlit run "%PROJECT_DIR%\%DASHBOARD%"

set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo ==========================================
    echo Dashboard stopped with an error.
    echo Error code: %EXIT_CODE%
    echo ==========================================
    echo.
    pause
)

endlocal & exit /b %EXIT_CODE%