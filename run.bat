@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Setup do projeto

:: Garante que o script rode na pasta onde ele esta
cd /d "%~dp0"

set "VENV_DIR=venv"
set "CONFIG=%~dp0banco.txt"

REM ======================================================================
REM  [1/4] Ambiente virtual
REM ======================================================================
echo [1/4] Verificando ambiente virtual...
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Criando ambiente virtual em '%VENV_DIR%'...
    python -m venv %VENV_DIR%
    if errorlevel 1 (
        echo [ERRO] Falha ao criar o ambiente virtual. Verifique se o Python esta instalado.
        goto error
    )
)

REM ======================================================================
REM  [2/4] Ativar venv
REM ======================================================================
echo [2/4] Ativando ambiente virtual...
call "%VENV_DIR%\Scripts\activate.bat"

REM ======================================================================
REM  [3/4] Dependencias
REM ======================================================================
echo [3/4] Instalando dependencias do 'requisitos.txt'...
if exist "requisitos.txt" (
    python -m pip install --upgrade pip
    pip install -r requisitos.txt
) else (
    echo [AVISO] O arquivo 'requisitos.txt' nao foi encontrado. Pulando instalacao.
)

REM ======================================================================
REM  [4/4] Rodando!
REM ======================================================================
echo [4/4] Rodando API e interface
if exist "run.py" (
    python run.py
) else (
    echo [AVISO] O arquivo 'run.py' nao foi encontrado!
)