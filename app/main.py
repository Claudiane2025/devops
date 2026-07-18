from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.responses import PlainTextResponse

from datetime import datetime

import requests
import logging


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("log_aula")


LISTA_TAREFAS = []


# ==========================
# MÉTRICAS
# ==========================

TOTAL_REQUISICOES = 0
TOTAL_TAREFAS_CRIADAS = 0
TOTAL_TAREFAS_ATUALIZADAS = 0
TOTAL_TAREFAS_REMOVIDAS = 0

TEMPOS_CONCLUSAO = []


APP = FastAPI()



# ==========================
# MIDDLEWARE
# ==========================

@APP.middleware("http")
async def log_requests(request, call_next):

    global TOTAL_REQUISICOES

    TOTAL_REQUISICOES += 1

    logger.info(
        f"Acesso à rota: {request.method} {request.url.path}"
    )

    response = await call_next(request)

    return response



# ==========================
# AUXILIARES
# ==========================

def nova_tarefa(id: int, titulo: str, descricao: str):

    return {
        "id": id,
        "titulo": titulo,
        "descricao": descricao,
        "concluido": False,
        "criado_em": datetime.now(),
        "concluido_em": None
    }



def verificar_existencia_tarefa(id: int):

    for tarefa in LISTA_TAREFAS:

        if id == tarefa["id"]:
            return True

    return False



# ==========================
# ROTAS
# ==========================


@APP.get("/")
def index():

    return "Olá, DevOps!"



# ==========================
# MÉTRICAS
# ==========================

@APP.get("/metrics", response_class=PlainTextResponse)
def metrics():


    total_tarefas = len(LISTA_TAREFAS)


    tarefas_concluidas = len(
        [
            tarefa
            for tarefa in LISTA_TAREFAS
            if tarefa["concluido"]
        ]
    )


    tarefas_pendentes = (
        total_tarefas -
        tarefas_concluidas
    )


    if len(TEMPOS_CONCLUSAO) > 0:

        tempo_medio = (
            sum(TEMPOS_CONCLUSAO)
            /
            len(TEMPOS_CONCLUSAO)
        )

    else:

        tempo_medio = 0



    return f"""
# HELP requisicoes_total Total de requisicoes
# TYPE requisicoes_total counter
requisicoes_total {TOTAL_REQUISICOES}


# HELP tarefas_total Total de tarefas cadastradas
# TYPE tarefas_total gauge
tarefas_total {total_tarefas}


# HELP tarefas_pendentes Total de tarefas pendentes
# TYPE tarefas_pendentes gauge
tarefas_pendentes {tarefas_pendentes}


# HELP tarefas_concluidas Total de tarefas concluídas
# TYPE tarefas_concluidas gauge
tarefas_concluidas {tarefas_concluidas}


# HELP tarefas_criadas_total Total de tarefas criadas
# TYPE tarefas_criadas_total counter
tarefas_criadas_total {TOTAL_TAREFAS_CRIADAS}


# HELP tarefas_atualizadas_total Total de atualizações
# TYPE tarefas_atualizadas_total counter
tarefas_atualizadas_total {TOTAL_TAREFAS_ATUALIZADAS}


# HELP tarefas_removidas_total Total de tarefas removidas
# TYPE tarefas_removidas_total counter
tarefas_removidas_total {TOTAL_TAREFAS_REMOVIDAS}


# HELP tarefa_tempo_medio_conclusao_segundos Tempo médio para concluir tarefas
# TYPE tarefa_tempo_medio_conclusao_segundos gauge
tarefa_tempo_medio_conclusao_segundos {tempo_medio}
"""



# ==========================
# LISTAR TAREFAS
# ==========================

@APP.get("/tarefas")
def listar_tarefas():


    if len(LISTA_TAREFAS) == 0:

        return LISTA_TAREFAS


    tarefas = []


    for tarefa in LISTA_TAREFAS:

        tarefas.append(
            {
                "id": tarefa["id"],
                "titulo": tarefa["titulo"]
            }
        )


    return tarefas




@APP.get("/tarefas/{id}")
def listar_tarefa_especifica(id: int):


    for tarefa in LISTA_TAREFAS:

        if tarefa["id"] == id:

            return tarefa


    return {
        "mensagem": "Não existe nenhuma tarefa"
    }




# ==========================
# CRIAR TAREFA
# ==========================

@APP.post("/tarefas", status_code=201)
def criar_tarefa(
        id: int,
        titulo: str,
        descricao: str):


    global TOTAL_TAREFAS_CRIADAS


    if verificar_existencia_tarefa(id):

        logger.error(
            f"Tentativa de criar tarefa existente ID={id}"
        )

        raise HTTPException(
            status_code=202,
            detail={
                "mensagem": "TAREFA JÁ EXISTE!"
            }
        )


    tarefa = nova_tarefa(
        id,
        titulo,
        descricao
    )


    LISTA_TAREFAS.append(tarefa)


    TOTAL_TAREFAS_CRIADAS += 1


    logger.info(
        f"Tarefa criada ID={id}"
    )


    return {
        "mensagem": "OK"
    }





# ==========================
# ATUALIZAR TAREFA
# ==========================

@APP.put("/tarefas/{id}")
def atualizar_tarefa(
        id: int,
        titulo: str = "",
        descricao: str = "",
        concluido: bool = False):


    global TOTAL_TAREFAS_ATUALIZADAS


    for tarefa in LISTA_TAREFAS:


        if tarefa["id"] == id:


            if titulo:

                tarefa["titulo"] = titulo


            if descricao:

                tarefa["descricao"] = descricao



            if concluido and not tarefa["concluido"]:


                agora = datetime.now()


                tarefa["concluido_em"] = agora


                tempo = (
                    agora -
                    tarefa["criado_em"]
                ).total_seconds()


                TEMPOS_CONCLUSAO.append(
                    tempo
                )


                try:

                    requests.post(
                        f"http://notificacoes:8000/notificar?"
                        f"titulo={tarefa['titulo']}"
                        f"&data_finalizacao={agora}",
                        timeout=10
                    )

                except Exception as e:

                    logger.error(e)



            tarefa["concluido"] = concluido


            TOTAL_TAREFAS_ATUALIZADAS += 1


            return {
                "mensagem": "OK"
            }



    return {
        "mensagem": "TAREFA NÃO EXISTE!"
    }





# ==========================
# REMOVER TAREFA
# ==========================

@APP.delete("/tarefas/{id}")
def apagar_tarefa(id: int):


    global TOTAL_TAREFAS_REMOVIDAS



    for indice, tarefa in enumerate(LISTA_TAREFAS):


        if tarefa["id"] == id:


            LISTA_TAREFAS.pop(indice)


            TOTAL_TAREFAS_REMOVIDAS += 1


            return {
                "mensagem": "OK"
            }



    return {
        "mensagem": "TAREFA NÃO EXISTE"
    }