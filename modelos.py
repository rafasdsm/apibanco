
from pydantic import BaseModel

class Cliente(BaseModel):
    nome: str
    email:str
    senha:str
    telefone:str
    endereco:str
    cpf:str