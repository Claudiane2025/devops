from fastapi.testclient import TestClient

from app import APP

CLIENT = TestClient(APP)

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