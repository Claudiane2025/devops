from fastapi import FastAPI
from fastapi.exceptions import HTTPException

from datetime import datetime

import requests
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("log_aula")

LISTA_TAREFAS = []
APP = FastAPI()

@APP.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Acesso à rota: {request.method} {request.url.path}")

    response = await call_next(request)

    return response

def nova_tarefa(id: int, titulo: str, descricao: str):
    """Função auxiliar para criar uma tarefa usando dicionário (`dict`)"""
    return {
        "id": id,
        "titulo": titulo,
        "descricao": descricao,
        "concluido": False,
        "criado_em": datetime.now()
    }

def verificar_existencia_tarefa(id: int):
    """Função auxiliar para verificar a existência de uma tarefa com base no seu ID"""
    for tarefa in LISTA_TAREFAS:
        if id == tarefa['id']:
            return True
    return False

@APP.get("/")
def index():
    return "Olá, DevOps!"

@APP.get("/tarefas")
def listar_tarefas():
    # Lista tarefas (somente id e titulo)
    if len(LISTA_TAREFAS) == 0:
        return LISTA_TAREFAS

    tarefas = []
    
    for tarefa in LISTA_TAREFAS:
        info = {"id": tarefa['id'], "titulo": tarefa['titulo']}
        tarefas.append(info)

    return tarefas

@APP.get("/tarefas/{id}")
def listar_tarefa_especifica(id: int):
    mensagem_padrao = {"mensagem": "Não existe nenhuma tarefa"}
    if len(LISTA_TAREFAS) == 0:
        return mensagem_padrao
    
    # ID da tarefa é o índice na lista
    if id >= 0 and id < len(LISTA_TAREFAS):
        return LISTA_TAREFAS[id]
    
    return mensagem_padrao

# Implementar!
# @APP.post("/tarefas")
# Rota /tarefas (POST)
#   Entrada: id da tarefa (int), titulo da tarefa (str) e descrição da tarefa (str)
#   Funcionamento:
#       - Recebe os dados como parâmetro de requisição
#       - Cria uma nova tarefa usando a função `nova_tarefa`
#       - Adiciona nova tarefa a LISTA_TAREFAS
#   # Saída:
#       - Retorna "OK" se a tarefa foi criada
#       - Se a tarefa existir, retornar "TAREFA JÁ EXISTE"

@APP.post("/tarefas", status_code=201)
def criar_tarefa(id: int, titulo: str, descricao: str):
    global LISTA_TAREFAS

    tarefa_existe = verificar_existencia_tarefa(id)

    if tarefa_existe:
        logger.error(f"Tentativa de criar tarefa existente: ID={id}")
        ex = HTTPException(status_code=202, detail={"mensagem": "TAREFA JÁ EXISTE!"})
        raise ex
    
    nova = nova_tarefa(id, titulo, descricao)

    LISTA_TAREFAS.append(nova)
    logger.info(f"Tarefa criada: ID={id}")
    logger.debug(f"Dados da tarefa: {nova}")

    return {"mensagem": "OK"}

# @APP.put("/tarefas/{id}")
# Rota /tarefas/{id} (PUT)
#   Entrada: id da tarefa (int), titulo da tarefa (str), descrição da tarefa (str) e concluido (bool)
#   Funcionamento:
#       - Recebe os dados como parâmetro de requisição
#       - Atualiza informações da tarefa de id específico
#   # Saída:
#       - Retorna "OK" se a tarefa foi atualizada
#       - Se a tarefa NÃO existir, retornar "TAREFA NÃO EXISTE"
@APP.put("/tarefas/{id}")
def atualizar_tarefa(id: int, titulo: str = "", descricao: str = "", concluido: bool = False):
    global LISTA_TAREFAS

    tarefa_existe = verificar_existencia_tarefa(id)

    if not tarefa_existe:
        return {"mensagem": "TAREFA NÃO EXISTE!"}
    
    tarefa = None
    for indice in range(len(LISTA_TAREFAS)):
        tarefa = LISTA_TAREFAS[indice]

        # Sai do loop
        if tarefa['id'] == id:
            break
    
    if titulo != "":
        LISTA_TAREFAS[indice]['titulo'] = titulo
    
    if descricao !=  "":
        LISTA_TAREFAS[indice]['descricao'] = descricao
    
    if concluido == True:
        requests.post(
            f"http://notificacoes:8000/notificar?titulo={tarefa['titulo']}&data_finalizacao={datetime.now()}",
            timeout=10
        )

    LISTA_TAREFAS[indice]['concluido'] = concluido

    return {"mensagem": "OK"}

# @APP.delete("/tarefas")
# Rota /tarefas/{id} (DELETE)
#   Entrada: id da tarefa (int)
#   Funcionamento:
#       - Recebe os dados como parâmetro de requisição
#       - Busca pela tarefa com base no ID
#       - Se tarefa existir, remover de LISTA_TAREFAS
#       - Se NÃO existir, retorna "TAREFA NÃO EXISTE"
#   # Saída:
#       - Retorna "OK" se a tarefa foi removida
#       - Se a tarefa NÃO existir, retornar "TAREFA NÃO EXISTE"
@APP.delete("/tarefas/{id}")
def apagar_tarefa(id: int):
    global LISTA_TAREFAS

    tarefa_existe = verificar_existencia_tarefa(id)

    if not tarefa_existe:
        return {"mensagem": "TAREFA NÃO EXISTE"}

    tarefa = None
    for indice in range(len(LISTA_TAREFAS)):
        tarefa = LISTA_TAREFAS[indice]

        # Sai do loop
        if tarefa['id'] == id:
            break
    
    LISTA_TAREFAS.pop(indice)

    return {"mensagem": "OK"}