
@echo off
setlocal

title Highlander Windows Builder

echo ==========================================
echo          HIGHLANDER BUILD SYSTEM
echo ==========================================
echo.

cd /d "%~dp0"

echo [1/5] Checking Python environment...

if not exist .venv (
    py -3.11 -m venv .venv
    if errorlevel 1 goto error
)

call .venv\Scripts\activate.bat
if errorlevel 1 goto error

echo.
echo [2/5] Updating pip...

python -m pip install --upgrade pip
if errorlevel 1 goto error

echo.
echo [3/5] Installing project dependencies...

pip install -r requirements.txt
if errorlevel 1 goto error

echo.
echo [4/5] Installing PyInstaller...

pip install pyinstaller
if errorlevel 1 goto error

echo.
echo [5/5] Building Highlander.exe...

pyinstaller --noconfirm --clean --windowed --onefile ^
--name Highlander ^
--collect-all google.genai ^
--collect-all keyring ^
src\main.py

if errorlevel 1 goto error

echo.
echo ==========================================
echo       HIGHLANDER BUILD SUCCESSFUL
echo ==========================================
echo.
echo Executable created:
echo %CD%\dist\Highlander.exe
echo.
echo You can now compile installer\Highlander.iss
echo using Inno Setup 6.
echo.
pause
exit /b 0

:error
echo.
echo ==========================================
echo             BUILD FAILED
echo ==========================================
echo Please check the error messages above.
echo.
pause
exit /b 1
