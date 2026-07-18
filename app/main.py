from fastapi import FastAPI
from fastapi.exceptions import HTTPException

from datetime import datetime, timedelta

import requests
import logging
import os

level = os.environ.get("LOG_LEVEL", logging.INFO)

if level == "DEBUG":
    level = logging.DEBUG
else:
    level = logging.INFO

LISTA_TAREFAS = []
APP = FastAPI()

LOGGER = logging.getLogger("DevOps")
LOGGER.setLevel(level)

stream_handler = logging.StreamHandler()
file_handler   = logging.FileHandler("api.log", encoding='utf-8')
fmt = logging.Formatter(fmt="%(name)s | %(asctime)s | %(filename)s:%(lineno)s | %(levelname)s | %(message)s")

stream_handler.setFormatter(fmt)
file_handler.setFormatter(fmt)

LOGGER.addHandler(stream_handler)
LOGGER.addHandler(file_handler)

#   - Quantidade total de tarefas
#   - Quantidade de tarefas pendentes
#   - Quantidade de tarefas concluídas
#   - Quantidade de tarefas atualizadas
#   - Quantidade de tarefas removidas
#   - Tempo médio para conclusão de tarefa

METRICAS = {
    'qtde_tarefas': 0,
    'qtde_tarefas_pendentes': 0,
    'qtde_tarefas_concluidas': 0,
    'qtde_tarefas_atualizadas': 0,
    'qtde_tarefas_removidas': 0,
    'tempo_medio_conclusao_tafefa': 0,
}

def nova_tarefa(id: int, titulo: str, descricao: str):
    """Função auxiliar para criar uma tarefa usando dicionário (`dict`)"""
    tarefa = {
        "id": id,
        "titulo": titulo,
        "descricao": descricao,
        "concluido": False,
        "criado_em": datetime.now(),
        "concluido_em": None
    }

    LOGGER.debug(f"Criando tarefa='{str(tarefa)}'")

    return tarefa

def verificar_existencia_tarefa(id: int):
    """Função auxiliar para verificar a existência de uma tarefa com base no seu ID"""
    for tarefa in LISTA_TAREFAS:
        if id == tarefa['id']:
            return True
    return False

@APP.get("/")
def index():
    LOGGER.info(f"Rota '/' foi acessada")
    return "Olá, DevOps!"

@APP.get("/tarefas")
def listar_tarefas():
    # Lista tarefas (somente id e titulo)
    
    LOGGER.info(f"Rota '/tarefas' foi acessada")

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
        LOGGER.error(f"Rota '/tarefas/{id} acessada. Mensagem: {mensagem_padrao['mensagem']}")
        return mensagem_padrao
    
    # ID da tarefa é o índice na lista
    if id >= 0 and id < len(LISTA_TAREFAS):
        LOGGER.info(f"Rota '/tarefas/{id} acessada.")
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
    global LISTA_TAREFAS, METRICAS

    tarefa_existe = verificar_existencia_tarefa(id)

    if tarefa_existe:
        ex = HTTPException(status_code=202, detail={"mensagem": "TAREFA JÁ EXISTE!"})
        LOGGER.error(f"Rota POST '/tarefas/' acessada. Tarefa já existe.")
        raise ex
    
    nova = nova_tarefa(id, titulo, descricao)

    LISTA_TAREFAS.append(nova)

    LOGGER.info(f"Rota POST '/tarefas' acessada. Tarefa id={id} criada.")

    METRICAS['qtde_tarefas'] += 1

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
    global LISTA_TAREFAS, METRICAS

    tarefa_existe = verificar_existencia_tarefa(id)

    if not tarefa_existe:
        LOGGER.error(f"Rota PUT '/tarefas/{id}' acessada. Tarefa NÃO existe.")
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
        METRICAS['qtde_tarefas_concluidas'] += 1
        LISTA_TAREFAS[indice]['concluido_em'] = datetime.now()

        # requests.post(
        #     f"http://notificacoes:8000/notificar?titulo={tarefa['titulo']}&data_finalizacao={datetime.now()}",
        #     timeout=10
        # )

    LISTA_TAREFAS[indice]['concluido'] = concluido

    LOGGER.debug(f"Tarefa atualizada = {LISTA_TAREFAS[indice]}")
    LOGGER.info(f"Rota PUT '/tarefas/{id}' acessada. Tarefa id={id} atualizada.")

    METRICAS['qtde_tarefas_atualizadas'] += 1
    METRICAS['qtde_tarefas_pendentes'] = METRICAS['qtde_tarefas'] - METRICAS['qtde_tarefas_concluidas']
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
    global LISTA_TAREFAS, METRICAS

    tarefa_existe = verificar_existencia_tarefa(id)

    if not tarefa_existe:
        LOGGER.error(f"Rota PUT '/tarefas/{id}' acessada. Tarefa NÃO existe.")
        return {"mensagem": "TAREFA NÃO EXISTE"}

    tarefa = None
    for indice in range(len(LISTA_TAREFAS)):
        tarefa = LISTA_TAREFAS[indice]

        # Sai do loop
        if tarefa['id'] == id:
            break
    
    LISTA_TAREFAS.pop(indice)

    LOGGER.info(f"Rota DELETE '/tarefas/{id}' acessada. Tarefa id={id} removida.")
    
    METRICAS['qtde_tarefas_removidas'] += 1
    METRICAS['qtde_tarefas'] -= 1

    return {"mensagem": "OK"}

# 20 minutos para desenvolver!
# @APP.get('/metricas')
# Retorne todas as métricas de negócio
#   - Quantidade total de tarefas
#   - Quantidade de tarefas pendentes
#   - Quantidade de tarefas concluídas
#   - Quantidade de tarefas atualizadas
#   - Quantidade de tarefas removidas
#   - Tempo médio para conclusão de tarefa
# Saída:
#   - Retornar um dicionário com os valores calculados 
# Pontos importantes:
#    - Criar testes unitários para validar se a contabilização está correta (criar arquivo tests/test_metricas.py)
#    - Incluir log de acesso à rota! (LOGGER.info)
@APP.get("/metricas")
def metricas():
    tempo_medio_total = timedelta()
    
    for tarefa in LISTA_TAREFAS:
        if tarefa['concluido']:
            tempo_medio = tarefa['concluido_em'] - tarefa['criado_em']
            tempo_medio_total += tempo_medio

    if METRICAS['qtde_tarefas_concluidas'] > 0:
        METRICAS['tempo_medio_conclusao_tarefa'] = tempo_medio_total / METRICAS['qtde_tarefas_concluidas']
    
    LOGGER.debug(METRICAS)
    LOGGER.info("Rota '/metricas' acessada.")

    return METRICAS