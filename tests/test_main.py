from fastapi.testclient import TestClient

from app import APP

CLIENT = TestClient(APP)

def criar_tarefa_mock():
    requisicao = CLIENT.post("/tarefas?id=0&titulo=tarefa&descricao=descricao-tarefa")

def test_index():
    requisicao = CLIENT.get("/")

    assert requisicao.status_code == 200
    assert requisicao.json() == "Olá, DevOps!"

def test_criar_tarefa():
    requisicao = CLIENT.post("/tarefas?id=0&titulo=tarefa&descricao=descricao-tarefa")

    assert requisicao.status_code == 201
    assert requisicao.json() == {"mensagem": "OK"}

    requisicao = CLIENT.post("/tarefas?id=0&titulo=tarefa&descricao=descricao-tarefa")
    assert requisicao.status_code == 202
    assert requisicao.json()['detail'] == {"mensagem": "TAREFA JÁ EXISTE!"}

def test_remover_tarefa():
    criar_tarefa_mock()

    requisicao = CLIENT.delete("/tarefas/0")
    assert requisicao.status_code == 200
    assert requisicao.json() == {"mensagem": "OK"}

    requisicao = CLIENT.delete("/tarefas/10")
    assert requisicao.status_code == 200
    assert requisicao.json() == {"mensagem": "TAREFA NÃO EXISTE"}

def test_atualizar_tarefa():
    criar_tarefa_mock()

    requisicao = CLIENT.put("/tarefas/0?id=0&titulo=tarefa_mock")
    assert requisicao.status_code == 200
    assert requisicao.json() == {"mensagem": "OK"}

    requisicao = CLIENT.get("/tarefas/0")
    assert requisicao.status_code == 200
    assert requisicao.json()["titulo"] == "tarefa_mock"


