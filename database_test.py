import argparse
import hashlib
import os
import random
import re
import struct
import sys
import unicodedata
import zlib
from datetime import datetime, timedelta
from decimal import Decimal

ARQUIVO_CONFIG = "banco.txt"
SENHA_PADRAO = "senha123"  # senha de todos os usuários fake (ou o hash dela com --hash)

# ----------------------------------------------------------------------------
# Dados de referência
# ----------------------------------------------------------------------------
NOMES = ["Ana", "Bruno", "Carla", "Daniel", "Eduarda", "Felipe", "Gabriela", "Henrique",
         "Isabela", "João", "Karen", "Lucas", "Mariana", "Nicolas", "Olívia", "Pedro",
         "Quitéria", "Rafael", "Sofia", "Thiago", "Valentina", "Wesley", "Yasmin", "Zeca",
         "Beatriz", "Caio", "Débora", "Eduardo", "Fernanda", "Gustavo", "Helena", "Igor",
         "Juliana", "Kauê", "Larissa", "Matheus", "Natália", "Otávio", "Patrícia", "Rodrigo"]
SOBRENOMES = ["Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira",
              "Lima", "Gomes", "Costa", "Ribeiro", "Martins", "Carvalho", "Almeida", "Lopes",
              "Soares", "Fernandes", "Vieira", "Barbosa", "Rocha", "Dias", "Nascimento",
              "Andrade", "Moreira", "Nunes", "Marques", "Machado", "Mendes", "Freitas"]
DOMINIOS = ["gmail.com", "outlook.com", "hotmail.com", "yahoo.com.br", "exemplo.com.br"]
RUAS = ["Rua das Flores", "Avenida Brasil", "Rua XV de Novembro", "Rua São Paulo",
        "Avenida Paulista", "Rua das Palmeiras", "Rua Sete de Setembro", "Alameda Santos",
        "Rua Harmonia", "Avenida Independência", "Rua dos Ipês", "Rua Santa Catarina"]
BAIRROS = ["Centro", "Jardim América", "Vila Nova", "Bela Vista", "Santa Cruz",
           "Jardim das Acácias", "Vila Mariana", "Cidade Nova", "São José", "Boa Vista"]
CIDADES = [("São Paulo", "SP"), ("Campinas", "SP"), ("Vinhedo", "SP"), ("Rio de Janeiro", "RJ"),
           ("Belo Horizonte", "MG"), ("Curitiba", "PR"), ("Porto Alegre", "RS"),
           ("Salvador", "BA"), ("Recife", "PE"), ("Florianópolis", "SC")]

MARCAS = ["Aurora", "Nexus", "Vértice", "Orion", "Prisma", "Atlas", "Zenith", "Lumina",
          "Titan", "Nova", "Sigma", "Delta"]
MODELOS = ["Pro", "Plus", "Lite", "Max", "X200", "S10", "Classic", "Premium", "Essencial", "2026"]
ADJETIVOS = ["durável", "moderno", "leve", "resistente", "elegante", "prático",
             "confortável", "versátil", "compacto", "de alta qualidade"]

# categoria -> lista de (item, tipo, preço mínimo, preço máximo)
CATALOGO = {
    "Eletrônicos": [("Smartphone", "Celular", 900, 6000), ("Fone de Ouvido Bluetooth", "Áudio", 80, 900),
                    ("Smart TV 50\"", "Televisão", 1800, 4500), ("Caixa de Som Portátil", "Áudio", 120, 1200),
                    ("Smartwatch", "Wearable", 250, 2500)],
    "Informática": [("Notebook", "Computador", 2500, 9000), ("Mouse Sem Fio", "Periférico", 30, 250),
                    ("Teclado Mecânico", "Periférico", 150, 900), ("Monitor 24\"", "Monitor", 700, 2200),
                    ("SSD 1TB", "Armazenamento", 280, 750)],
    "Casa e Cozinha": [("Air Fryer", "Eletroportátil", 250, 900), ("Jogo de Panelas", "Utensílios", 150, 800),
                       ("Liquidificador", "Eletroportátil", 90, 450), ("Cafeteira", "Eletroportátil", 120, 700),
                       ("Aspirador de Pó", "Limpeza", 200, 1100)],
    "Moda": [("Camiseta", "Vestuário", 40, 150), ("Calça Jeans", "Vestuário", 90, 300),
             ("Tênis Casual", "Calçado", 150, 600), ("Jaqueta", "Vestuário", 160, 550),
             ("Mochila", "Acessório", 80, 350)],
    "Esportes": [("Bola de Futebol", "Futebol", 50, 250), ("Bicicleta Aro 29", "Ciclismo", 1200, 4500),
                 ("Halteres 10kg", "Musculação", 90, 320), ("Tapete de Yoga", "Fitness", 45, 180),
                 ("Garrafa Térmica", "Acessório", 40, 160)],
    "Livros": [("Romance Best-Seller", "Ficção", 25, 80), ("Guia de Programação", "Técnico", 70, 220),
               ("Livro de Receitas", "Culinária", 40, 120), ("Biografia", "Não-ficção", 35, 100),
               ("Box de Mangá", "Quadrinhos", 90, 350)],
    "Beleza": [("Perfume", "Fragrância", 90, 600), ("Kit de Skincare", "Cuidados com a pele", 80, 450),
               ("Secador de Cabelo", "Eletro beleza", 100, 500), ("Paleta de Sombras", "Maquiagem", 50, 250),
               ("Shampoo Premium", "Cabelo", 25, 120)],
    "Brinquedos": [("Bloco de Montar", "Construção", 60, 400), ("Boneca Articulada", "Bonecas", 40, 220),
                   ("Carrinho de Controle Remoto", "Veículos", 90, 450), ("Quebra-Cabeça 1000 peças", "Jogos", 45, 160),
                   ("Jogo de Tabuleiro", "Jogos", 80, 350)],
}
GENERICO = [("Produto", "Geral", 20, 500)]

STATUS_PEDIDO = [("Novo", "pendente", 20), ("Pago", "pago", 20), ("Enviado", "pago", 20),
                 ("Entregue", "pago", 30), ("Cancelado", "cancelado", 10)]
FORMAS_PAGAMENTO = ["Cartão de crédito", "Cartão de débito", "Pix", "Boleto"]


# ----------------------------------------------------------------------------
# Utilitários
# ----------------------------------------------------------------------------
def q(nome: str) -> str:
    """Coloca o identificador entre colchetes de forma segura."""
    return "[" + nome.replace("]", "]]") + "]"


def slug(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", texto.lower())


def cortar(texto: str, limite: int) -> str:
    return texto if len(texto) <= limite else texto[:limite].rstrip()


def nome_completo() -> str:
    return f"{random.choice(NOMES)} {random.choice(SOBRENOMES)} {random.choice(SOBRENOMES)}"


def email_unico(nome: str, usados: set) -> str:
    partes = nome.split()
    while True:
        email = f"{slug(partes[0])}.{slug(partes[-1])}{random.randint(1, 9999)}@{random.choice(DOMINIOS)}"
        if email not in usados:
            usados.add(email)
            return cortar(email, 100)


def gerar_cpf(usados: set) -> str:
    """CPF válido (dígitos verificadores corretos), 11 caracteres, único."""
    while True:
        n = [random.randint(0, 9) for _ in range(9)]
        if len(set(n)) == 1:
            continue
        for _ in range(2):
            soma = sum(d * w for d, w in zip(n, range(len(n) + 1, 1, -1)))
            n.append((soma * 10) % 11 % 10)
        cpf = "".join(map(str, n))
        if cpf not in usados:
            usados.add(cpf)
            return cpf


def gerar_telefone() -> str:
    return f"({random.randint(11, 99)}) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"


def gerar_endereco() -> str:
    cidade, uf = random.choice(CIDADES)
    return cortar(
        f"{random.choice(RUAS)}, {random.randint(1, 3000)}, {random.choice(BAIRROS)}, "
        f"{cidade} - {uf}, CEP {random.randint(10000, 99999)}-{random.randint(100, 999)}", 255)


def senha(usar_hash: bool) -> str:
    return hashlib.sha256(SENHA_PADRAO.encode()).hexdigest() if usar_hash else SENHA_PADRAO


def gerar_png(cor, tam: int = 64) -> bytes:
    """PNG válido de cor sólida, sem depender de bibliotecas externas."""
    def chunk(tipo: bytes, dados: bytes) -> bytes:
        corpo = tipo + dados
        return struct.pack(">I", len(dados)) + corpo + struct.pack(">I", zlib.crc32(corpo) & 0xFFFFFFFF)

    linha = b"\x00" + bytes(cor) * tam
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", tam, tam, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(linha * tam))
            + chunk(b"IEND", b""))


def inserir(cur, tabela: str, dados: dict, retorno: str = None):
    """INSERT parametrizado; devolve o valor de `retorno` (ex.: id gerado) se pedido."""
    colunas = ", ".join(q(c) for c in dados)
    placeholders = ", ".join("?" for _ in dados)
    saida = f" OUTPUT INSERTED.{q(retorno)}" if retorno else ""
    cur.execute(f"INSERT INTO dbo.{q(tabela)} ({colunas}){saida} VALUES ({placeholders})",
                tuple(dados.values()))
    if retorno:
        return cur.fetchone()[0]


def valores_existentes(cur, tabela: str, coluna: str) -> set:
    cur.execute(f"SELECT {q(coluna)} FROM dbo.{q(tabela)}")
    return {str(r[0]).strip().lower() if coluna == "email" else str(r[0]).strip() for r in cur.fetchall()}


def colunas_da_tabela(cur, tabela: str) -> set:
    cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?", (tabela,))
    return {r[0].lower() for r in cur.fetchall()}


# ----------------------------------------------------------------------------
# Geradores (um por tabela / grupo de endpoints)
# ----------------------------------------------------------------------------
def gerar_admins(cur, qtd: int, usar_hash: bool) -> None:
    usados = valores_existentes(cur, "admins", "email")
    for _ in range(qtd):
        nome = nome_completo()
        inserir(cur, "admins", {"nome": cortar(nome, 100),
                                "email": email_unico(nome, usados),
                                "senha": senha(usar_hash)})
    print(f"  admins: {qtd}")


def gerar_categorias(cur, qtd: int) -> None:
    existentes = valores_existentes(cur, "categorias", "nome")
    existentes = {e.lower() for e in existentes}
    disponiveis = [c for c in CATALOGO if c.lower() not in existentes]
    escolhidas = random.sample(disponiveis, min(qtd, len(disponiveis)))
    for nome in escolhidas:
        inserir(cur, "categorias", {"nome": cortar(nome, 50)})
    print(f"  categorias: {len(escolhidas)}")


def gerar_clientes(cur, qtd: int, usar_hash: bool) -> None:
    emails = valores_existentes(cur, "clientes", "email")
    cpfs = valores_existentes(cur, "clientes", "cpf")
    for _ in range(qtd):
        nome = nome_completo()
        inserir(cur, "clientes", {
            "nome": cortar(nome, 100),
            "email": email_unico(nome, emails),
            "senha": senha(usar_hash),
            "telefone": gerar_telefone(),
            "endereco": gerar_endereco(),
            "cpf": gerar_cpf(cpfs),
        })
    print(f"  clientes: {qtd}")


def gerar_produtos(cur, qtd: int) -> None:
    cur.execute("SELECT categoria_id, nome FROM dbo.categorias")
    categorias = [(r[0], r[1]) for r in cur.fetchall()]
    if not categorias:
        print("  produtos: nenhuma categoria existe, pulando.")
        return

    colunas = colunas_da_tabela(cur, "produtos")
    tem_blob = {"imagem_byte", "imagem_nome", "imagem_tipo"} <= colunas
    nomes_usados = set()

    for _ in range(qtd):
        cat_id, cat_nome = random.choice(categorias)
        item, tipo, pmin, pmax = random.choice(CATALOGO.get(cat_nome, GENERICO))

        for _tentativa in range(20):
            nome = cortar(f"{item} {random.choice(MARCAS)} {random.choice(MODELOS)}", 100)
            if nome not in nomes_usados:
                break
        nomes_usados.add(nome)

        quantidade = 0 if random.random() < 0.10 else random.randint(1, 500)
        dados = {
            "categoria_id": cat_id,
            "nome": nome,
            "descricao": cortar(f"{nome}: produto {random.choice(ADJETIVOS)} e {random.choice(ADJETIVOS)}, "
                                f"ideal para o seu dia a dia. Garantia de 12 meses.", 255),
            "preco": Decimal(random.randint(pmin, pmax)) - Decimal("0.10"),  # termina em ,90
            "disponivel": quantidade > 0 and random.random() > 0.05,
            "quantidade_disponivel": quantidade,
        }
        if "tipo" in colunas:
            dados["tipo"] = cortar(tipo, 100)

        # A API grava a imagem em imagem_byte/nome/tipo; o schema do script de
        # criação usa imagem_url. Cobrimos os dois casos conforme o banco real.
        if tem_blob:
            cor = tuple(random.randint(40, 220) for _ in range(3))
            dados.update({"imagem_byte": gerar_png(cor),
                          "imagem_nome": cortar(f"{slug(nome)}.png", 255),
                          "imagem_tipo": "image/png"})
        elif "imagem_url" in colunas:
            dados["imagem_url"] = cortar(f"https://placehold.co/600x400?text={slug(item)}", 255)

        inserir(cur, "produtos", dados)
    print(f"  produtos: {qtd}")


def gerar_pedidos(cur, qtd: int) -> None:
    cur.execute("SELECT cliente_id, endereco FROM dbo.clientes")
    clientes = [(r[0], r[1]) for r in cur.fetchall()]
    cur.execute("SELECT produto_id, preco FROM dbo.produtos")
    produtos = [(r[0], Decimal(str(r[1]))) for r in cur.fetchall()]
    if not clientes or not produtos:
        print("  pedidos: precisa de clientes e produtos, pulando.")
        return

    status_lista = [(s, p) for s, p, _ in STATUS_PEDIDO]
    pesos = [w for _, _, w in STATUS_PEDIDO]
    agora = datetime.now()
    total_itens = 0

    for _ in range(qtd):
        cliente_id, endereco_cliente = random.choice(clientes)
        status, status_pag = random.choices(status_lista, weights=pesos)[0]
        data = (agora - timedelta(days=random.randint(0, 365), hours=random.randint(0, 23),
                                  minutes=random.randint(0, 59))).replace(microsecond=0)

        itens = []
        for produto_id, preco in random.sample(produtos, min(random.randint(1, 5), len(produtos))):
            itens.append((produto_id, random.randint(1, 4), preco))
        valor_total = sum((preco * qtd_item for _, qtd_item, preco in itens), Decimal("0.00"))

        # 80% entregam no endereço cadastrado, 20% em outro
        endereco = cortar(endereco_cliente, 255) if random.random() < 0.8 else gerar_endereco()

        pedido_id = inserir(cur, "pedidos", {
            "cliente_id": cliente_id,
            "data_pedido": data,
            "status": status,
            "valor_total": valor_total,
            "endereco_entrega": endereco,
            "forma_pagamento": random.choice(FORMAS_PAGAMENTO),
            "status_pagamento": status_pag,
        }, retorno="pedido_id")

        for produto_id, qtd_item, preco in itens:
            inserir(cur, "itenspedido", {"pedido_id": pedido_id, "produto_id": produto_id,
                                         "quantidade": qtd_item, "preco_unitario": preco})
        total_itens += len(itens)
    print(f"  pedidos: {qtd} (itenspedido: {total_itens})")


def limpar_tabelas(cur) -> None:
    """Apaga tudo na ordem inversa das FKs e reinicia os IDENTITY."""
    ordem = [("itenspedido", 0), ("pedidos", 0), ("produtos", 0),
             ("clientes", 0), ("categorias", 129), ("admins", 0)]  # categorias começa em 130
    for tabela, semente in ordem:
        cur.execute(f"DELETE FROM dbo.{q(tabela)}")
        cur.execute(f"DBCC CHECKIDENT ('dbo.{tabela}', RESEED, {semente})")
    print("  tabelas limpas.")


# ----------------------------------------------------------------------------
# Conexão e execução
# ----------------------------------------------------------------------------
def carregar_config() -> dict:
    cfg = {}
    if os.path.exists(ARQUIVO_CONFIG):
        with open(ARQUIVO_CONFIG, encoding="utf-8") as f:
            for linha in f:
                if "=" in linha:
                    k, v = linha.split("=", 1)
                    cfg[k.strip().lower()] = v.strip()
    return cfg


def montar_conn_str() -> str:
    cfg = carregar_config()
    servidor = os.getenv("MSSQL_SERVER") or cfg.get("server") or "localhost"
    banco = os.getenv("MSSQL_DB") or cfg.get("database") or "site"
    usuario = os.getenv("MSSQL_USER", "")
    partes = [f"Server={servidor}", f"Database={banco}", "Encrypt=no"]
    if usuario:
        partes += [f"UID={usuario}", f"PWD={os.getenv('MSSQL_PASSWORD', '')}"]
    else:
        partes.append("Trusted_Connection=yes")
    return ";".join(partes) + ";"


def gerar_dados() -> int:
    ap = argparse.ArgumentParser(description="Gerador de dados fake para o banco 'site'.")
    ap.add_argument("--admins", type=int, default=2)
    ap.add_argument("--categorias", type=int, default=8, help=f"máx. {len(CATALOGO)} distintas")
    ap.add_argument("--clientes", type=int, default=50)
    ap.add_argument("--produtos", type=int, default=80)
    ap.add_argument("--pedidos", type=int, default=120)
    ap.add_argument("--seed", type=int, help="semente para resultados reproduzíveis")
    ap.add_argument("--limpar", action="store_true", help="apaga todos os dados antes de gerar")
    ap.add_argument("--hash", action="store_true", help="grava senhas como SHA-256 em vez de texto puro")
    args = ap.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    from mssql_python import connect  # import tardio: só é necessário para conectar

    try:
        conn = connect(montar_conn_str())
    except Exception as err:
        print(f"Erro ao conectar ao banco: {err}", file=sys.stderr)
        return 1

    try:
        cur = conn.cursor()
        print("Gerando dados...")
        if args.limpar:
            limpar_tabelas(cur)
        gerar_admins(cur, args.admins, args.hash)
        gerar_categorias(cur, args.categorias)
        gerar_clientes(cur, args.clientes, args.hash)
        gerar_produtos(cur, args.produtos)
        gerar_pedidos(cur, args.pedidos)
        conn.commit()  # tudo ou nada
        print(f"Concluído. Senha dos usuários fake: {SENHA_PADRAO}"
              + (" (gravada como SHA-256)" if args.hash else ""))
        return 0
    except Exception as err:
        conn.rollback()
        print(f"Erro ao gerar dados, nada foi gravado: {err}", file=sys.stderr)
        return 1
    finally:
        conn.close()


