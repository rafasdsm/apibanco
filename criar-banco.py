import pyodbc

# Remove o prefixo ::SQL:: e limpa o texto
script_sql = """
IF DB_ID(N'site') IS NULL
    CREATE DATABASE [site] COLLATE Latin1_General_CI_AS;
GO
USE [site];
GO

IF OBJECT_ID(N'dbo.admins', N'U') IS NULL
CREATE TABLE dbo.admins (
    admin_id INT IDENTITY PRIMARY KEY,
    nome     VARCHAR(100) NOT NULL,
    email    VARCHAR(100) NOT NULL UNIQUE,
    senha    VARCHAR(255) NOT NULL
);
GO
-- (continue colando o restante do script aqui ou leia de um arquivo .sql)
"""

# Conexão com o SQL Server (ajuste a string conforme seu ambiente)
conexao = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"  # Note a barra dupla no Python
    "DATABASE=site;"
    "Trusted_connection=yes;"
)
conexao.autocommit = True
cursor = conexao.cursor()

# O sqlcmd/pyodbc às vezes precisa lidar com o comando GO separadamente.
# Dividindo por GO:
comandos = script_sql.split("GO")

for comando in comandos:
  if comando.strip():
    cursor.execute(comando)

print("Banco de dados e tabelas criados com sucesso!")