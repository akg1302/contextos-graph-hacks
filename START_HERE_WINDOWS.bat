@echo off
setlocal
cd /d "%~dp0"
echo ============================================================
echo  ContextOS - Graph Hacks 2026
echo  Cloud mode: no Docker or WSL required
echo ============================================================
echo.
where py >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python launcher 'py' was not found.
  echo Install Python 3.11 or newer from https://www.python.org/downloads/
  echo During installation, enable the option to add Python to PATH.
  pause
  exit /b 1
)
if not exist ".env" (
  echo First setup required: copy .env.example to .env and fill in your FalkorDB Cloud connection details.
  echo Open https://www.falkordb.com/try-free/ and create a free instance.
  echo Do not send your password or connection secrets in chat.
  echo.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo [1/3] Creating Python virtual environment...
  py -m venv .venv
  if errorlevel 1 goto failed
)
echo [2/3] Installing Python dependencies...
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo [3/3] Starting ContextOS. Keep this window open.
echo When Streamlit starts, open http://localhost:8501 in your browser.
.venv\Scripts\python.exe -m streamlit run streamlit_app.py
if errorlevel 1 goto failed
exit /b 0
:failed
echo.
echo Something did not start correctly. Send a screenshot, but hide all secrets.
pause
exit /b 1
