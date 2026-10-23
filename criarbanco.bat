@echo off
cls
echo ====================================================
echo   Criando Banco de Dados no SQL Server Express...
echo ====================================================

:: Nome da instância padrão do SQL Server Express
set SERVER_NAME=.\SQLEXPRESS
set SCRIPT_NAME=schema.sql

echo Tentando conectar via Autenticação do Windows (sem senha)...
sqlcmd -S %SERVER_NAME% -E -i "%SCRIPT_NAME%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCESSO] Banco de dados e tabelas criados com sucesso!
) else (
    echo.
    echo [AVISO] Falha ao conectar em %SERVER_NAME%. Tentando na instancia padrao (localhost)...
    sqlcmd -S "localhost" -E -i "%SCRIPT_NAME%"
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo [SUCESSO] Banco de dados criado usando a instancia local!
    ) else (
        echo.
        echo [ERRO] Nao foi possivel criar o banco automaticamente.
        echo Verifique se o servico do SQL Server (SQLEXPRESS) esta ligado.
    )
)

echo.
pause