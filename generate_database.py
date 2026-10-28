import os
import re
import sys

from mssql_python import connect

SERVER_ENV = os.getenv("MSSQL_SERVER", "").strip()
PORT = os.getenv("MSSQL_PORT", "1433").strip()
DB_NAME = os.getenv("MSSQL_DB", "site")
USER = os.getenv("MSSQL_USER", "")
PASSWORD = os.getenv("MSSQL_PASSWORD", "")

SERVER = ""  # filled in by find_server()

# Schema batches (the original GO separators become list items).
SCHEMA_BATCHES = [
    """
IF OBJECT_ID(N'dbo.admins', N'U') IS NULL
CREATE TABLE dbo.admins (
    admin_id INT IDENTITY PRIMARY KEY,
    nome     VARCHAR(100) NOT NULL,
    email    VARCHAR(100) NOT NULL UNIQUE,
    senha    VARCHAR(255) NOT NULL
);
""",
    """
IF OBJECT_ID(N'dbo.categorias', N'U') IS NULL
CREATE TABLE dbo.categorias (
    categoria_id INT IDENTITY(130,1) PRIMARY KEY,
    nome         VARCHAR(50) NOT NULL
);
""",
    """
IF OBJECT_ID(N'dbo.clientes', N'U') IS NULL
CREATE TABLE dbo.clientes (
    cliente_id INT IDENTITY PRIMARY KEY,
    nome       VARCHAR(100) NOT NULL,
    email      VARCHAR(100) NOT NULL UNIQUE,
    senha      VARCHAR(100) NOT NULL,
    telefone   VARCHAR(20)  NOT NULL,
    endereco   VARCHAR(500) NOT NULL,
    cpf        CHAR(11)     NOT NULL UNIQUE
);
""",
    """
IF OBJECT_ID(N'dbo.produtos', N'U') IS NULL
CREATE TABLE dbo.produtos (
    produto_id            INT IDENTITY PRIMARY KEY,
    categoria_id          INT NOT NULL
        CONSTRAINT FK_produtos_categoria REFERENCES dbo.categorias,
    nome                  VARCHAR(100)   NOT NULL,
    descricao             VARCHAR(255)   NOT NULL,
    preco                 DECIMAL(10,2)  NOT NULL,
    disponivel            BIT DEFAULT 1,
    imagem_url            VARCHAR(255),
    quantidade_disponivel INT DEFAULT 0  NOT NULL,
    tipo                  VARCHAR(100)
);
""",
    """
IF OBJECT_ID(N'dbo.pedidos', N'U') IS NULL
CREATE TABLE dbo.pedidos (
    pedido_id        INT IDENTITY PRIMARY KEY,
    cliente_id       INT NOT NULL
        CONSTRAINT FK_pedidos_cliente REFERENCES dbo.clientes,
    data_pedido      DATETIME NOT NULL,
    status           VARCHAR(50) DEFAULT 'Novo' NOT NULL,
    valor_total      DECIMAL(10,2),
    endereco_entrega VARCHAR(255) NOT NULL,
    forma_pagamento  VARCHAR(50),
    status_pagamento VARCHAR(30) DEFAULT 'pendente'
);
""",
    """
IF OBJECT_ID(N'dbo.itenspedido', N'U') IS NULL
CREATE TABLE dbo.itenspedido (
    item_id        INT IDENTITY PRIMARY KEY,
    pedido_id      INT NOT NULL
        CONSTRAINT FK_itenspedido_pedido REFERENCES dbo.pedidos,
    produto_id     INT NOT NULL
        CONSTRAINT FK_itenspedido_produto REFERENCES dbo.produtos,
    quantidade     INT NOT NULL,
    preco_unitario DECIMAL(10,2) NOT NULL
);
""",
]


def quote_ident(name: str) -> str:
    """Safely bracket-quote a SQL Server identifier."""
    return "[" + name.replace("]", "]]") + "]"


def build_conn_str(database: str, server: str = "") -> str:
    parts = [
        f"SERVER={server or SERVER}",
        f"DATABASE={database}",
        "Encrypt=yes",
        "TrustServerCertificate=yes",  # remove in production with a valid cert
    ]
    if USER:
        parts += [f"UID={USER}", f"PWD={PASSWORD}"]
    else:
        parts.append("Trusted_Connection=yes")
    return ";".join(parts)


def candidate_servers() -> list[str]:
    """Server addresses to try, forcing TCP so Named Pipes is never used."""
    if SERVER_ENV:
        s = SERVER_ENV
        has_protocol = s.lower().startswith(("tcp:", "np:", "lpc:"))
        if has_protocol or "," in s or "\\" in s:
            return [s]  # explicit port / named instance / protocol: use as-is
        return [f"tcp:{s},{PORT}", s]
    return [
        f"tcp:localhost,{PORT}",
        "tcp:127.0.0.1," + PORT,
        "localhost\\SQLEXPRESS",
        "(localdb)\\MSSQLLocalDB",
    ]


def find_server() -> str:
    """Return the first server address that accepts a connection."""
    global SERVER
    errors = []
    for server in candidate_servers():
        try:
            conn = connect(build_conn_str("master", server), autocommit=True)
            conn.close()
            SERVER = server
            print(f"Connected to: {server}")
            return server
        except Exception as exc:
            errors.append(f"  - {server}: {exc}")
    raise RuntimeError(
        "Could not connect to SQL Server. Tried:\n"
        + "\n".join(errors)
        + "\n\nChecklist: SQL Server service running? TCP/IP enabled in "
        "Configuration Manager? SQL Server Browser running (named instances)? "
        "Correct MSSQL_SERVER / MSSQL_PORT / credentials (mixed-mode auth for SQL logins)?"
    )


def create_database() -> None:
    # CREATE DATABASE cannot run inside a transaction -> autocommit=True
    conn = connect(build_conn_str("master"), autocommit=True)
    try:
        cur = conn.cursor()
        cur.execute("SELECT DB_ID(?)", (DB_NAME,))
        exists = cur.fetchone()[0] is not None
        if exists:
            print(f"Database '{DB_NAME}' already exists.")
        else:
            cur.execute(
                f"CREATE DATABASE {quote_ident(DB_NAME)} COLLATE Latin1_General_CI_AS"
            )
            print(f"Database '{DB_NAME}' created.")
    finally:
        conn.close()


def create_tables() -> None:
    conn = connect(build_conn_str(DB_NAME), autocommit=False)
    try:
        cur = conn.cursor()
        for batch in SCHEMA_BATCHES:
            table = re.search(r"dbo\.(\w+)", batch).group(1)
            cur.execute(batch)
            print(f"  table dbo.{table}: ok")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def generate_database() -> int:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", DB_NAME):
        print("Invalid database name; use letters, digits and underscores.")
        return 1
    try:
        find_server()
        create_database()
        create_tables()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(generate_database())