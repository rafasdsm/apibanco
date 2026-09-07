from fastapi import FastAPI
from database import Dbcontroller
from modelos import Cliente, Produtos, Categorias, Pedidos
from datetime import datetime


db = Dbcontroller()
app = FastAPI()
tabelas = [
    "clientes",
    "produtos",
    "categorias",
    "pedidos"
]


@app.get("/")
def read_root():
    return db.ler_banco()


@app.post("/inserir_cliente")
def inserir_cliente(cliente:Cliente):
    dado = {
        "nome":cliente.nome,
        "email":cliente.email,
        "senha":cliente.senha,
        "telefone":cliente.telefone,
        "endereco":cliente.endereco,
        "cpf":cliente.cpf}
    response = db.inserir_tabela(tabelas[0],dado)
    return {"message":response}

@app.post("/remover_cliente")
def remover_cliente(identificador_nome,identificador_):
    response = db.remover_de_tabela(tabelas[0],indentificador_nome=identificador_nome,identificador=identificador_)
    return {"message":response}

@app.post("/inserir_produto") #criar rota para inserir produto
def inserir_produto(produto:Produtos):
    dado = {
        "categoria_id":produto.categoria_id,
        "nome":produto.nome,
        "descricao":produto.descricao,
        "preco":produto.preco,
        "disponivel":produto.disponivel,
        "imagem_url":produto.imagem_url,
        "quantidade_disponivel":produto.quantidade_disponivel}
    response = db.inserir_tabela(tabelas[1],dado)
    return {"message":response}
@app.post("/remover_produto") #criar rota para remover produto
def remover_produto(identificador_nome,identificador_):
    response = db.remover_de_tabela(tabelas[1],indentificador_nome=identificador_nome,identificador=identificador_)
    return {"message":response}


@app.post("/inserir_categoria") #criar rota para inserir categoria
def inserir_categoria(categoria:Categorias):
    dado = {
        "nome":categoria.nome}
    response = db.inserir_tabela(tabelas[2],dado)
    return {"message":response}
@app.post("/remover_categoria") #criar rota para remover categoria
def remover_categoria(identificador_nome,identificador_):
    response = db.remover_de_tabela(tabelas[2],indentificador_nome=identificador_nome,identificador=identificador_)
    return {"message":response}

@app.post("/inserir_pedido") #criar rota para inserir pedido
def inserir_pedido(pedido:Pedidos):
    dado = {
        "cliente_id":pedido.cliente_id,
        "data_pedido":pedido.data_pedido or datetime.now(),
        "endereco_entrega":pedido.endereco_entrega,
        "forma_pagamento":pedido.forma_pagamento}
    response = db.inserir_tabela(tabelas[3],dado)
    return {"message":response}
@app.post("/remover_pedido") #criar rota para remover pedido
def remover_pedido(identificador_nome,identificador_):  
    response = db.remover_de_tabela(tabelas[3],indentificador_nome=identificador_nome,identificador=identificador_)
    return {"message":response}