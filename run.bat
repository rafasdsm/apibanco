@echo off
setlocal

:: Define o caminho da venv
set "VENV_DIR=venv"

echo [1/5] Verificando ambiente virtual...
if not exist "%VENV_DIR%\Scripts\activate.bat" (
echo Criando ambiente virtual em '%VENV_DIR%'...
python -m venv %VENV_DIR%
if errorlevel 1 (
echo [ERRO] Falha ao criar o ambiente virtual. Verifique se o Python esta instalado.
goto error
)
)

echo [2/5] Ativando ambiente virtual...
call "%VENV_DIR%\Scripts\activate.bat"

echo [3/4] Instalando dependencias do 'requisitos.txt'...
if exist "requisitos.txt" (
python -m pip install --upgrade pip
pip install -r requisitos.txt
) else (
echo [AVISO] O arquivo 'requisitos.txt' nao foi encontrado. Pulando instalacao.
)

echo [4/5] criando banco ...

@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Criar banco de dados "site"

REM ======================================================================
REM  Cria o banco "site" (admins, categorias, clientes, produtos,
REM  pedidos, itenspedido) no SQL Server.
REM
REM  Autenticacao: Windows (sqlcmd -E). NAO pede usuario nem senha;
REM  usa a conta do Windows que executa o script.
REM
REM  Uso:  criar_banco_site.bat                 (detecta o servidor)
REM        criar_banco_site.bat "localhost\SQLEXPRESS"
REM ======================================================================

where sqlcmd >nul 2>&1
if errorlevel 1 (
    echo [ERRO] sqlcmd nao encontrado. Instale o "SQL Server Command Line Utilities"
    echo        ou o SQL Server Management Studio e tente novamente.
    pause & exit /b 1
)

set "SERVIDOR=%~1"

if not defined SERVIDOR (
    echo Procurando instancia do SQL Server...
    for %%S in ("localhost" ".\SQLEXPRESS" "(localdb)\MSSQLLocalDB" ".") do (
        if not defined SERVIDOR (
            sqlcmd -S %%~S -E -l 3 -Q "SELECT 1" >nul 2>&1
            if not errorlevel 1 set "SERVIDOR=%%~S"
        )
    )
)

if not defined SERVIDOR (
    echo [ERRO] Nenhuma instancia do SQL Server respondeu com autenticacao do Windows.
    echo        Informe o servidor manualmente:
    echo        %~nx0 "NOME_DO_PC\INSTANCIA"
    pause & exit /b 1
)

echo Servidor: %SERVIDOR%

REM --- Extrai o SQL embutido no final deste arquivo para um temporario ---
set "SQLFILE=%TEMP%\criar_banco_site_%RANDOM%.sql"
if exist "%SQLFILE%" del "%SQLFILE%"
for /f "usebackq delims=" %%L in (`findstr /b /c:"::SQL::" "%~f0"`) do (
    set "linha=%%L"
    >>"%SQLFILE%" echo(!linha:~7!
)

echo Criando banco de dados...
sqlcmd -S "%SERVIDOR%" -E -b -i "%SQLFILE%"
set "RESULT=%ERRORLEVEL%"
del "%SQLFILE%" >nul 2>&1

if not "%RESULT%"=="0" (
    echo.
    echo [ERRO] Falha ao criar o banco ^(codigo %RESULT%^).
    echo        Verifique se sua conta do Windows tem permissao de CREATE DATABASE.
    pause & exit /b %RESULT%
)


::SQL::IF DB_ID(N'site') IS NULL
::SQL::    CREATE DATABASE [site] COLLATE Latin1_General_CI_AS;
::SQL::GO
::SQL::USE [site];
::SQL::GO
::SQL::
::SQL::IF OBJECT_ID(N'dbo.admins', N'U') IS NULL
::SQL::CREATE TABLE dbo.admins (
::SQL::    admin_id INT IDENTITY PRIMARY KEY,
::SQL::    nome     VARCHAR(100) NOT NULL,
::SQL::    email    VARCHAR(100) NOT NULL UNIQUE,
::SQL::    senha    VARCHAR(255) NOT NULL
::SQL::);
::SQL::GO
::SQL::
::SQL::IF OBJECT_ID(N'dbo.categorias', N'U') IS NULL
::SQL::CREATE TABLE dbo.categorias (
::SQL::    categoria_id INT IDENTITY(130,1) PRIMARY KEY,
::SQL::    nome         VARCHAR(50) NOT NULL
::SQL::);
::SQL::GO
::SQL::
::SQL::IF OBJECT_ID(N'dbo.clientes', N'U') IS NULL
::SQL::CREATE TABLE dbo.clientes (
::SQL::    cliente_id INT IDENTITY PRIMARY KEY,
::SQL::    nome       VARCHAR(100) NOT NULL,
::SQL::    email      VARCHAR(100) NOT NULL UNIQUE,
::SQL::    senha      VARCHAR(100) NOT NULL,
::SQL::    telefone   VARCHAR(20)  NOT NULL,
::SQL::    endereco   VARCHAR(500) NOT NULL,
::SQL::    cpf        CHAR(11)     NOT NULL UNIQUE
::SQL::);
::SQL::GO
::SQL::
::SQL::IF OBJECT_ID(N'dbo.produtos', N'U') IS NULL
::SQL::CREATE TABLE dbo.produtos (
::SQL::    produto_id            INT IDENTITY PRIMARY KEY,
::SQL::    categoria_id          INT NOT NULL
::SQL::        CONSTRAINT FK_produtos_categoria REFERENCES dbo.categorias,
::SQL::    nome                  VARCHAR(100)   NOT NULL,
::SQL::    descricao             VARCHAR(255)   NOT NULL,
::SQL::    preco                 DECIMAL(10,2)  NOT NULL,
::SQL::    disponivel            BIT DEFAULT 1,
::SQL::    imagem_url            VARCHAR(255),
::SQL::    quantidade_disponivel INT DEFAULT 0  NOT NULL,
::SQL::    tipo                  VARCHAR(100)
::SQL::);
::SQL::GO
::SQL::
::SQL::IF OBJECT_ID(N'dbo.pedidos', N'U') IS NULL
::SQL::CREATE TABLE dbo.pedidos (
::SQL::    pedido_id        INT IDENTITY PRIMARY KEY,
::SQL::    cliente_id       INT NOT NULL
::SQL::        CONSTRAINT FK_pedidos_cliente REFERENCES dbo.clientes,
::SQL::    data_pedido      DATETIME NOT NULL,
::SQL::    status           VARCHAR(50) DEFAULT 'Novo' NOT NULL,
::SQL::    valor_total      DECIMAL(10,2),
::SQL::    endereco_entrega VARCHAR(255) NOT NULL,
::SQL::    forma_pagamento  VARCHAR(50),
::SQL::    status_pagamento VARCHAR(30) DEFAULT 'pendente'
::SQL::);
::SQL::GO
::SQL::
::SQL::IF OBJECT_ID(N'dbo.itenspedido', N'U') IS NULL
::SQL::CREATE TABLE dbo.itenspedido (
::SQL::    item_id        INT IDENTITY PRIMARY KEY,
::SQL::    pedido_id      INT NOT NULL
::SQL::        CONSTRAINT FK_itenspedido_pedido REFERENCES dbo.pedidos,
::SQL::    produto_id     INT NOT NULL
::SQL::        CONSTRAINT FK_itenspedido_produto REFERENCES dbo.produtos,
::SQL::    quantidade     INT NOT NULL,
::SQL::    preco_unitario DECIMAL(10,2) NOT NULL
::SQL::);
::SQL::GO

echo [5/5] Iniciando FastAPI...
:: Tenta usar o comando fastapi direto, se falhar usa o uvicorn via python
fastapi dev
if errorlevel 1 (
python -m uvicorn main:app --reload
)

goto end

:error
echo.
echo Ocorreu um erro durante a execucao do script.

:end
pause
endlocal