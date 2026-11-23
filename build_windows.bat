@echo off
setlocal
cd /d "%~dp0"
if not exist .venv (
  py -3 -m venv .venv
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
pyinstaller --noconfirm --clean --windowed --onefile --name GeminiDesktopOperator --collect-all google.genai --collect-all keyring src\main.py
echo.
echo Build complete: dist\GeminiDesktopOperator.exe
pause
