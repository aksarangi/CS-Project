@echo off
:: ================================================================
::  BOOKSHOP MANAGEMENT SYSTEM – FULL ENVIRONMENT SETUP
::  Author: Abheek Kumar Sarangi
:: ================================================================

title Bookshop Management System Setup
color 0A
echo ===============================================================
echo            BOOKSHOP MANAGEMENT SYSTEM SETUP SCRIPT
echo ===============================================================
echo.

:: ---------- Enable ANSI colors ----------
for /f "tokens=2 delims=: " %%A in ('"echo prompt $E|cmd"') do set "ESC=%%A"

set "STEP=%ESC%[37m[STEP]%ESC%[0m"
set "INFO=%ESC%[36m[INFO]%ESC%[0m"
set "WARN=%ESC%[91m[WARN]%ESC%[0m"
set "OK=%ESC%[32m[OK]%ESC%[0m"
set "ERROR=%ESC%[31m[ERROR]%ESC%[0m"

:: ---------- Detect project root ----------
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"
echo %STEP% Project root set to: %PROJECT_ROOT%
echo.

:: ---------- Folder structure creation ----------
echo %STEP% Creating folder structure...
mkdir backend 2>nul
mkdir backend\api 2>nul
mkdir backend\database 2>nul
mkdir backend\models 2>nul
mkdir backend\utils 2>nul
mkdir frontend 2>nul
mkdir logs 2>nul
echo %OK% Folder structure verified.
echo.

:: ---------- Python setup ----------
echo %STEP% Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo %ERROR% Python not found. Please install Python and rerun.
    pause
    exit /b
)
echo %OK% Python detected.
echo.

:: ---------- Requirements.txt ----------
if not exist "requirements.txt" (
    echo %STEP% Creating requirements.txt...
    (
        echo flask
        echo flask-cors
        echo mysql-connector-python
        echo python-dotenv
    ) > requirements.txt
    echo %OK% requirements.txt created.
) else (
    echo %INFO% requirements.txt already exists — skipping.
)
echo.

:: ---------- Install Python dependencies ----------
echo %STEP% Installing dependencies to global Python environment...
pip install -r requirements.txt
if errorlevel 1 (
    echo %ERROR% Dependency installation failed.
    pause
    exit /b
)
echo %OK% Python dependencies installed.
echo.

:: ---------- Handle .env file ----------
set "ENV_FILE=%PROJECT_ROOT%\.env"
if exist "%ENV_FILE%" (
    echo %INFO% .env file already exists.
    choice /C OKE /M "Do you want to (O)verwrite, (K)eep, or (E)dit credentials?"
    if errorlevel 3 (
        echo %STEP% Opening .env for manual editing...
        notepad "%ENV_FILE%"
    )
    if errorlevel 2 (
        echo %INFO% Keeping existing .env file.
    )
    if errorlevel 1 (
        echo %STEP% Overwriting .env file...
        del "%ENV_FILE%"
        goto CREATE_ENV
    )
) else (
    :CREATE_ENV
    echo %STEP% Creating new .env configuration...
    set /p DB_HOST="Enter MySQL host [default: localhost]: "
    if "%DB_HOST%"=="" set "DB_HOST=localhost"

    set /p DB_PORT="Enter MySQL port [default: 3306]: "
    if "%DB_PORT%"=="" set "DB_PORT=3306"

    set /p DB_USER="Enter MySQL username [default: root]: "
    if "%DB_USER%"=="" set "DB_USER=root"

    set /p DB_PASS="Enter MySQL password: "
    set /p DB_NAME="Enter database name [default: bookshop_db]: "
    if "%DB_NAME%"=="" set "DB_NAME=bookshop_db"

    (
        echo DB_HOST=%DB_HOST%
        echo DB_PORT=%DB_PORT%
        echo DB_USER=%DB_USER%
        echo DB_PASS=%DB_PASS%
        echo DB_NAME=%DB_NAME%
    ) > "%ENV_FILE%"
    echo %OK% .env created successfully.
)
echo.

:: ---------- MySQL Database Initialization ----------
echo %STEP% Initializing MySQL database...

:: Extract values from .env for MySQL
for /f "tokens=2 delims==" %%A in ('findstr "^DB_HOST=" ".env"') do set DB_HOST=%%A
for /f "tokens=2 delims==" %%A in ('findstr "^DB_PORT=" ".env"') do set DB_PORT=%%A
for /f "tokens=2 delims==" %%A in ('findstr "^DB_USER=" ".env"') do set DB_USER=%%A
for /f "tokens=2 delims==" %%A in ('findstr "^DB_PASS=" ".env"') do set DB_PASS=%%A
for /f "tokens=2 delims==" %%A in ('findstr "^DB_NAME=" ".env"') do set DB_NAME=%%A

echo %STEP% Creating database [%DB_NAME%]...
mysql -h %DB_HOST% -P %DB_PORT% -u %DB_USER% -p%DB_PASS% -e "CREATE DATABASE IF NOT EXISTS %DB_NAME%;"
if errorlevel 1 (
    echo %ERROR% Could not connect to MySQL or create DB. Check credentials.
    pause
    exit /b
)
echo %OK% Database verified or created.
echo.

:: ---------- Import SQL files if present ----------
set "INIT_SQL=backend\database\init_database.sql"
set "DATA_SQL=backend\database\sample_data.sql"

if exist "%INIT_SQL%" (
    echo %STEP% Importing schema from init_database.sql...
    mysql -h %DB_HOST% -P %DB_PORT% -u %DB_USER% -p%DB_PASS% %DB_NAME% < "%INIT_SQL%"
    echo %OK% Schema imported.
) else (
    echo %WARN% init_database.sql not found. Please add it manually to backend\database.
)

if exist "%DATA_SQL%" (
    echo %STEP% Importing synthetic data from sample_data.sql...
    mysql -h %DB_HOST% -P %DB_PORT% -u %DB_USER% -p%DB_PASS% %DB_NAME% < "%DATA_SQL%"
    echo %OK% Sample data imported.
) else (
    echo %WARN% sample_data.sql not found. Add it later and rerun this script.
)

:: ---------- Launch VS Code ----------
echo %STEP% Launching Visual Studio Code...
code "%PROJECT_ROOT%" >nul 2>&1
if errorlevel 1 (
    echo %WARN% VS Code not found in PATH. Please open manually.
) else (
    echo %OK% VS Code launched successfully.
)
echo.

echo ===============================================================
echo             %OK% SETUP COMPLETED SUCCESSFULLY
echo ===============================================================
echo.
pause
/p Press any key to exit: