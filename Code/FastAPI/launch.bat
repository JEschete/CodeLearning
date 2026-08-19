
@echo off
REM First we want to detect the python version and set the path to the virtual environment accordingly

REM The following command will get the version of Python installed on the system
setlocal enabledelayedexpansion 

REM %~dp0 = this script's own folder, so the script works no matter what directory it's launched from
set "SCRIPT_DIR=%~dp0"

REM PY_VER_NUM is major*100+minor (e.g. 313 for 3.13) so version comparisons are numeric, not per-version string branches
for /f "tokens=1,2" %%a in ('python -c "import sys; print('python' + str(sys.version_info[0]) + '.' + str(sys.version_info[1]) + ' ' + str(sys.version_info[0]*100 + sys.version_info[1]))"') do (
    set PYTHON_VERSION=%%a
    set PY_VER_NUM=%%b
)

REM Print the detected python version
echo Detected Python version: %PYTHON_VERSION%

REM All supported versions share the same venv, so only a single 3.10+ floor check is needed
if %PY_VER_NUM% LSS 310 (
    echo Unsupported Python version: %PYTHON_VERSION%
    exit /b 1
)
set VENV_NAME=fastapi

REM Build an absolute venv path so activation/pip/python calls work regardless of caller's cwd
set "VENV_PATH=%SCRIPT_DIR%%VENV_NAME%"

REM Now we create the virtual environment if it does not exist
if not exist "%VENV_PATH%" (
    echo Creating virtual environment at %VENV_PATH%
    python -m venv "%VENV_PATH%"
) else (
    echo Virtual environment already exists at %VENV_PATH%
)

REM Check if the virtual environment is running
if not defined VIRTUAL_ENV (
    echo Virtual environment is not running. 
    REM Now we activate the virtual environment
    call "%VENV_PATH%\Scripts\activate.bat"
) else (
    echo Virtual environment is running at %VIRTUAL_ENV%
)

REM check if the virtual environment was activated successfully
if "%VIRTUAL_ENV%"=="" (
    echo Failed to activate virtual environment at %VENV_PATH%
    exit /b 1
) else (
    echo Virtual environment activated at %VENV_PATH%
)

REM Use the python version installed in the virtual environment to run the FastAPI application
set PYTHON_EXE=%VENV_PATH%\Scripts\python.exe

REM Check the venv's own pip (not a possibly-different global pip on PATH)
%PYTHON_EXE% -m pip list | findstr /R /C:"fastapi" >nul
if %errorlevel% neq 0 (
    echo Installing required packages...
    %PYTHON_EXE% -m pip install -r "%SCRIPT_DIR%requirements.txt"
) else (
    echo Required packages are already installed.
)

REM main.py imports itself as Code.FastAPI.Lecture6_Project3.*, so it must be run with the repo root on sys.path
pushd "%SCRIPT_DIR%..\.."

REM Now we can run the FastAPI application
echo Starting FastAPI application...
%PYTHON_EXE% -m uvicorn Code.FastAPI.Lecture6_Project3.main:app --reload

popd