@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

rem ============================================================
rem  CONFIGURACOES (ajuste aqui se necessario)
rem ============================================================
set "SQL_SERVER=.\SQLEXPRESS"
set "DB_NAME=site"
set "VENV_DIR=%~dp0venv"
set "REQ_FILE=requisitos.txt"
set "SQL_FILE=%TEMP%\criar_tabelas_site.sql"

rem 1 = o script cria as tabelas logo apos criar o banco
rem 0 = cria so o banco vazio (use se o generate_data.py ja cria as tabelas)
set "CRIAR_TABELAS=1"

rem 1 = run.py abre em outra janela (use se for um servidor que nao termina)
rem 0 = espera o run.py terminar antes de abrir o interface.exe
set "RUN_EM_NOVA_JANELA=1"

set "DB_CRIADO=0"

echo ============================================================
echo  [1/6] Verificando banco de dados "%DB_NAME%"
echo ============================================================
where sqlcmd >nul 2>&1
if errorlevel 1 (
    echo ERRO: sqlcmd nao encontrado. Instale o "SQL Server Command Line Utilities".
    goto :erro
)

set "DB_EXISTE="
for /f "usebackq delims=" %%R in (`sqlcmd -S "%SQL_SERVER%" -E -C -h -1 -W -Q "SET NOCOUNT ON; SELECT COUNT(*) FROM sys.databases WHERE name = N'%DB_NAME%'" 2^>^&1`) do set "DB_EXISTE=%%R"

if "%DB_EXISTE%"=="1" (
    echo Banco "%DB_NAME%" ja existe. Criacao ignorada.
    goto :banco_ok
)
if not "%DB_EXISTE%"=="0" (
    echo ERRO: nao foi possivel consultar o SQL Server em "%SQL_SERVER%".
    echo Resposta: %DB_EXISTE%
    goto :erro
)

echo Banco nao encontrado. Criando "%DB_NAME%"...
sqlcmd -S "%SQL_SERVER%" -E -C -b -Q "CREATE DATABASE [%DB_NAME%]"
if errorlevel 1 (
    echo ERRO ao criar o banco de dados.
    goto :erro
)
set "DB_CRIADO=1"
echo Banco "%DB_NAME%" criado com sucesso.

if "%CRIAR_TABELAS%"=="1" (
    echo Criando tabelas...
    call :gerar_sql
    sqlcmd -S "%SQL_SERVER%" -E -C -b -d "%DB_NAME%" -i "%SQL_FILE%"
    if errorlevel 1 (
        del "%SQL_FILE%" >nul 2>&1
        echo ERRO ao criar as tabelas.
        goto :erro
    )
    del "%SQL_FILE%" >nul 2>&1
    echo Tabelas criadas com sucesso.
)

:banco_ok

echo.
echo ============================================================
echo  [2/6] Criando ambiente virtual
echo ============================================================
if exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Ambiente virtual ja existe.
) else (
    set "PY_CMD="
    where py >nul 2>&1 && set "PY_CMD=py -3"
    if not defined PY_CMD (
        where python >nul 2>&1 && set "PY_CMD=python"
    )
    if not defined PY_CMD (
        echo ERRO: Python nao encontrado no PATH.
        goto :erro
    )
    %PY_CMD% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo ERRO ao criar o ambiente virtual.
        goto :erro
    )
)

echo.
echo ============================================================
echo  [3/6] Ativando ambiente virtual
echo ============================================================
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo ERRO ao ativar o ambiente virtual.
    goto :erro
)

echo.
echo ============================================================
echo  [4/6] Instalando requisitos (%REQ_FILE%)
echo ============================================================
if not exist "%REQ_FILE%" (
    echo ERRO: %REQ_FILE% nao encontrado em %~dp0
    goto :erro
)
python -m pip install --upgrade pip
python -m pip install -r "%REQ_FILE%"
if errorlevel 1 (
    echo ERRO ao instalar os requisitos.
    goto :erro
)

echo.
echo ============================================================
echo  [5/6] Executando scripts Python
echo ============================================================
if "%DB_CRIADO%"=="1" (
    echo Banco recem-criado: executando generate_data.py...
    python generate_data.py
    if errorlevel 1 (
        echo ERRO ao executar generate_data.py.
        goto :erro
    )
) else (
    echo Banco ja existia: generate_data.py nao sera executado.
)

echo Executando run.py...
if "%RUN_EM_NOVA_JANELA%"=="1" (
    start "run.py" cmd /k ""%VENV_DIR%\Scripts\python.exe" run.py"
    timeout /t 5 /nobreak >nul
) else (
    python run.py
    if errorlevel 1 (
        echo ERRO ao executar run.py.
        goto :erro
    )
)

echo.
echo ============================================================
echo  [6/6] Abrindo interface.exe
echo ============================================================
if exist "%~dp0interface.exe" (
    start "" "%~dp0interface.exe"
) else (
    start "" interface.exe
    if errorlevel 1 (
        echo ERRO: interface.exe nao encontrado.
        goto :erro
    )
)

echo.
echo Tudo pronto.
endlocal
exit /b 0

:erro
echo.
echo O processo foi interrompido por um erro.
pause
endlocal
exit /b 1

rem ============================================================
rem  Gera o arquivo SQL com a estrutura das tabelas
rem ============================================================
:gerar_sql
>"%SQL_FILE%" echo IF OBJECT_ID(N'dbo.admins','U') IS NULL
>>"%SQL_FILE%" echo CREATE TABLE dbo.admins (
>>"%SQL_FILE%" echo     admin_id INT IDENTITY(1,1) PRIMARY KEY,
>>"%SQL_FILE%" echo     nome VARCHAR(100) NOT NULL,
>>"%SQL_FILE%" echo     email VARCHAR(150) NOT NULL UNIQUE,
>>"%SQL_FILE%" echo     senha VARCHAR(255) NOT NULL
>>"%SQL_FILE%" echo );
>>"%SQL_FILE%" echo IF OBJECT_ID(N'dbo.categorias','U') IS NULL
>>"%SQL_FILE%" echo CREATE TABLE dbo.categorias (
>>"%SQL_FILE%" echo     categoria_id INT IDENTITY(1,1) PRIMARY KEY,
>>"%SQL_FILE%" echo     nome VARCHAR(100) NOT NULL
>>"%SQL_FILE%" echo );
>>"%SQL_FILE%" echo IF OBJECT_ID(N'dbo.clientes','U') IS NULL
>>"%SQL_FILE%" echo CREATE TABLE dbo.clientes (
>>"%SQL_FILE%" echo     cliente_id INT IDENTITY(1,1) PRIMARY KEY,
>>"%SQL_FILE%" echo     nome VARCHAR(150) NOT NULL,
>>"%SQL_FILE%" echo     email VARCHAR(150) NOT NULL UNIQUE,
>>"%SQL_FILE%" echo     senha VARCHAR(255) NOT NULL,
>>"%SQL_FILE%" echo     telefone VARCHAR(30) NULL,
>>"%SQL_FILE%" echo     endereco VARCHAR(255) NULL,
>>"%SQL_FILE%" echo     cpf VARCHAR(14) NOT NULL UNIQUE
>>"%SQL_FILE%" echo );
>>"%SQL_FILE%" echo IF OBJECT_ID(N'dbo.produtos','U') IS NULL
>>"%SQL_FILE%" echo CREATE TABLE dbo.produtos (
>>"%SQL_FILE%" echo     produto_id INT IDENTITY(1,1) PRIMARY KEY,
>>"%SQL_FILE%" echo     categoria_id INT NULL,
>>"%SQL_FILE%" echo     nome VARCHAR(150) NOT NULL,
>>"%SQL_FILE%" echo     descricao VARCHAR(MAX) NULL,
>>"%SQL_FILE%" echo     preco DECIMAL(10,2) NOT NULL,
>>"%SQL_FILE%" echo     disponivel BIT NOT NULL DEFAULT 1,
>>"%SQL_FILE%" echo     quantidade_disponivel INT NOT NULL DEFAULT 0,
>>"%SQL_FILE%" echo     imagem_byte VARBINARY(MAX) NULL,
>>"%SQL_FILE%" echo     imagem_nome VARCHAR(255) NULL,
>>"%SQL_FILE%" echo     imagem_tipo VARCHAR(100) NULL,
>>"%SQL_FILE%" echo     CONSTRAINT FK_produtos_categoria FOREIGN KEY (categoria_id) REFERENCES dbo.categorias(categoria_id)
>>"%SQL_FILE%" echo );
>>"%SQL_FILE%" echo IF OBJECT_ID(N'dbo.pedidos','U') IS NULL
>>"%SQL_FILE%" echo CREATE TABLE dbo.pedidos (
>>"%SQL_FILE%" echo     pedido_id INT IDENTITY(1,1) PRIMARY KEY,
>>"%SQL_FILE%" echo     cliente_id INT NOT NULL,
>>"%SQL_FILE%" echo     data_pedido DATETIME NOT NULL DEFAULT GETDATE(),
>>"%SQL_FILE%" echo     status VARCHAR(30) NOT NULL DEFAULT 'pendente',
>>"%SQL_FILE%" echo     valor_total DECIMAL(10,2) NOT NULL,
>>"%SQL_FILE%" echo     endereco_entrega VARCHAR(255) NULL,
>>"%SQL_FILE%" echo     forma_pagamento VARCHAR(50) NULL,
>>"%SQL_FILE%" echo     status_pagamento VARCHAR(30) NOT NULL DEFAULT 'pendente',
>>"%SQL_FILE%" echo     CONSTRAINT FK_pedidos_cliente FOREIGN KEY (cliente_id) REFERENCES dbo.clientes(cliente_id)
>>"%SQL_FILE%" echo );
>>"%SQL_FILE%" echo IF OBJECT_ID(N'dbo.itenspedido','U') IS NULL
>>"%SQL_FILE%" echo CREATE TABLE dbo.itenspedido (
>>"%SQL_FILE%" echo     item_id INT IDENTITY(1,1) PRIMARY KEY,
>>"%SQL_FILE%" echo     pedido_id INT NOT NULL,
>>"%SQL_FILE%" echo     produto_id INT NOT NULL,
>>"%SQL_FILE%" echo     quantidade INT NOT NULL,
>>"%SQL_FILE%" echo     preco_unitario DECIMAL(10,2) NOT NULL,
>>"%SQL_FILE%" echo     CONSTRAINT FK_itenspedido_pedido FOREIGN KEY (pedido_id) REFERENCES dbo.pedidos(pedido_id),
>>"%SQL_FILE%" echo     CONSTRAINT FK_itenspedido_produto FOREIGN KEY (produto_id) REFERENCES dbo.produtos(produto_id)
>>"%SQL_FILE%" echo );
exit /b 0