@echo off
setlocal enabledelayedexpansion

REM Ensure the script runs from the project root.
cd /d %~dp0

REM Create a virtual environment if it does not exist.
if not exist .venv (
    echo Creating Python virtual environment...
    py -m venv .venv
    if errorlevel 1 goto error
)

REM Activate the virtual environment.
call .venv\Scripts\activate.bat
if errorlevel 1 goto error

REM Install dependencies.
echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 goto error

REM Optionally seed the database with mock data. Pass skip-mock to disable.
if /I "%1"=="skip-mock" (
    echo Skipping mock data generation.
) else (
    echo Seeding mock data into the database...
    python mock_data.py
    if errorlevel 1 echo Warning: mock data seeding failed, continuing...
)

echo Starting Streamlit application...
streamlit run app.py
goto end

:error
echo.
echo ERROR: Startup script failed.
pause

:end
endlocal
