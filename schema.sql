-- Criar o banco de dados caso não exista
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'LojaDB')
BEGIN
    CREATE DATABASE LojaDB;
END
GO

USE LojaDB;
GO

-- 1. Tabela Admins
CREATE TABLE admins
(
    admin_id INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    senha VARCHAR(255) NOT NULL,
    CONSTRAINT UQ_admins_email UNIQUE (email)
);

-- 2. Tabela Categorias
CREATE TABLE categorias
(
    categoria_id INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(50) NOT NULL
);

-- 3. Tabela Clientes
CREATE TABLE clientes
(
    cliente_id INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    senha VARCHAR(100) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    endereco VARCHAR(500) NOT NULL,
    cpf CHAR(11) NOT NULL,
    CONSTRAINT UQ_clientes_cpf UNIQUE (cpf),
    CONSTRAINT UQ_clientes_email UNIQUE (email)
);

-- 4. Tabela Pedidos
CREATE TABLE pedidos
(
    pedido_id INT IDENTITY(1,1) PRIMARY KEY,
    cliente_id INT NOT NULL,
    data_pedido DATETIME NOT NULL,
    status VARCHAR(50) DEFAULT 'Novo' NOT NULL,
    valor_total DECIMAL(10, 2) NULL,
    endereco_entrega VARCHAR(255) NOT NULL,
    forma_pagamento VARCHAR(50) NULL,
    status_pagamento VARCHAR(30) DEFAULT 'pendente' NULL,
    CONSTRAINT FK_pedidos_clientes FOREIGN KEY (cliente_id) REFERENCES clientes (cliente_id)
);

CREATE INDEX IX_pedidos_cliente_id ON pedidos (cliente_id);

-- 5. Tabela Produtos
CREATE TABLE produtos
(
    produto_id INT IDENTITY(1,1) PRIMARY KEY,
    categoria_id INT NOT NULL,
    nome VARCHAR(100) NOT NULL,
    descricao VARCHAR(255) NOT NULL,
    preco DECIMAL(10, 2) NOT NULL,
    disponivel BIT DEFAULT 1 NULL, -- Alterado de tinyint(1) para BIT
    imagem_url VARCHAR(255) NULL,
    quantidade_disponivel INT DEFAULT 0 NOT NULL,
    tipo VARCHAR(100) NULL,
    CONSTRAINT FK_produtos_categorias FOREIGN KEY (categoria_id) REFERENCES categorias (categoria_id)
);

CREATE INDEX IX_produtos_categoria_id ON produtos (categoria_id);

-- 6. Tabela ItensPedido
CREATE TABLE itenspedido
(
    item_id INT IDENTITY(1,1) PRIMARY KEY,
    pedido_id INT NOT NULL,
    produto_id INT NOT NULL,
    quantidade INT NOT NULL,
    preco_unitario DECIMAL(10, 2) NOT NULL,
    CONSTRAINT FK_itenspedido_pedidos FOREIGN KEY (pedido_id) REFERENCES pedidos (pedido_id),
    CONSTRAINT FK_itenspedido_produtos FOREIGN KEY (produto_id) REFERENCES produtos (produto_id)
);

CREATE INDEX IX_itenspedido_pedido_id ON itenspedido (pedido_id);
CREATE INDEX IX_itenspedido_produto_id ON itenspedido (produto_id);
GO