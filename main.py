from fastapi import FastAPI, UploadFile, File, Form
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
    return {"message":db.ler_banco()}

@app.get('/ler_tabela')
def read_tabela(tabela:str):
    return {"message":db.ler_tabela(tabela)}

###################################################################
#                                                                 #
#                            Clientes                             #
#                                                                 #
###################################################################

@app.get("/procurar_cliente")
def procurar_cliente(cliente_id:int):
    dado = ["cliente_id",cliente_id]
    response = db.procurar_tabela(dado,tabelas[0])

    response = {
        "message":list(response)
    }
    return response

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

@app.delete("/remover_cliente")
def remover_cliente(identificador_nome,identificador_):
    response = db.remover_de_tabela(tabelas[0],indentificador_nome=identificador_nome,identificador=identificador_)
    return {"message":response}

@app.patch("/alterar_cliente")
def alterar_cliente(id:int,coluna:str,dado):
    response = db.atualizar_tabela(tabela=tabelas[0],coluna=coluna,id=id,dado=dado,id_nome="cliente_id")
    return {"message":response}

###################################################################
#                                                                 #
#                            Produtos                             #
#                                                                 #
###################################################################

@app.get("/procurar_produto")
def procurar_produto(produto_id:int):
    dado = ["produto_id",produto_id]
    response = db.procurar_tabela(dado,tabelas[1])

    response = {
        "message":list(response)
    }
    return response


@app.post("/inserir_produtos")
async def inserir_produtos(
    categoria_id: int = Form(...),
    nome: str = Form(...),
    descricao: str = Form(...),
    preco: float = Form(...),
    disponivel: bool = Form(...),
    quantidade_disponivel: int = Form(...),
    imagem: UploadFile = File(...)
):
    dados_imagem = await imagem.read()

    dado = {
        "categoria_id":categoria_id,
        "descricao":descricao,
        "disponivel":disponivel,
        "preco":preco,
        "quantidade_disponivel":quantidade_disponivel,
        "imagem":dados_imagem,
        "nome":nome
}

    response = db.inserir_tabela("produtos",dado)
    return {
        "message":f"{dado['nome']} Adicionado com sucesso!"
    }

@app.delete("/remover_produto") #criar rota para remover produto
def remover_produto(identificador_nome,identificador_):
    response = db.remover_de_tabela(tabelas[1],indentificador_nome=identificador_nome,identificador=identificador_)
    return {"message":response}

@app.patch("/alterar_produto")
def alterar_produto(id:int,coluna:str,dado):
    return{
        "message":db.atualizar_tabela(
            coluna=coluna,
            dado=dado,
            tabela=tabelas[1],
            id=id,
            id_nome="produto_id",
        )
        }

###################################################################
#                                                                 #
#                            Categorias                           #
#                                                                 #
###################################################################

@app.get("/procurar_categoria")
def procurar_categoria(categoria_id:int):
    dado = ["categoria_id",categoria_id]
    response = db.procurar_tabela(dado,tabelas[2])

    response = {
        "message":list(response)
    }
    return response



@app.post("/inserir_categoria") #criar rota para inserir categoria
def inserir_categoria(categoria:Categorias):
    dado = {
        "nome":categoria.nome}
    response = db.inserir_tabela(tabelas[2],dado)
    return {"message":response}

@app.delete("/remover_categoria") #criar rota para remover categoria
def remover_categoria(identificador_nome,identificador_):
    response = db.remover_de_tabela(tabelas[2],indentificador_nome=identificador_nome,identificador=identificador_)
    return {"message":response}

@app.patch("/alterar_categoria")
def alterar_categoria(id:int,dado):
    return{
        "message":db.atualizar_tabela(
            coluna="nome",
            dado=dado,
            tabela=tabelas[2],
            id=id,
            id_nome="categoria_id"
        )
        }

###################################################################
#                                                                 #
#                            Pedidos                              #
#                                                                 #
###################################################################

@app.get("/procurar_pedidos")
def procurar_pedidos(pedidos_id:int):
    dado = ["pedidos_id",pedidos_id]
    response = db.procurar_tabela(dado,tabelas[3])

    response = {
        "message":list(response)
    }
    return response



@app.post("/inserir_pedido") #criar rota para inserir pedido
def inserir_pedido(pedido:Pedidos):
    dado = {
        "cliente_id":pedido.cliente_id,
        "data_pedido":pedido.data_pedido or datetime.now(),
        "endereco_entrega":pedido.endereco_entrega,
        "forma_pagamento":pedido.forma_pagamento}
    response = db.inserir_tabela(tabelas[3],dado)
    return {"message":response}

@app.delete("/remover_pedido") #criar rota para remover pedido
def remover_pedido(identificador_nome,identificador_):  
    response = db.remover_de_tabela(tabelas[3],indentificador_nome=identificador_nome,identificador=identificador_)
    return {"message":response}

@app.patch("/alterar_pedido")
def alterar_pedido(id:int,coluna:str,dado):

    return{
            "message":db.atualizar_tabela(
                coluna=coluna,
                dado=dado,
                tabela=tabelas[3],
                id=id,
                id_nome="pedido_id"
            )
            }


