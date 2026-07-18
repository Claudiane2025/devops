from fastapi.testclient import TestClient

from app import APP

CLIENT = TestClient(APP)

def criar_tarefa_mock():
    requisicao = CLIENT.post("/tarefas?id=0&titulo=tarefa&descricao=descricao-tarefa")

def test_index():
    requisicao = CLIENT.get("/")

    assert requisicao.status_code == 200
    assert requisicao.json() == "Olá, DevOps!"

# Criar um teste unitário para validar se a tarefa foi criada com sucesso
# CLIENT.post(...) (substituir pela string para criação de tarefa)
# Verificar se o código de status é 201
# Verificar se o retorno, quando tarefa é criada, é igual a {"mensagem": "OK"} ou conforme definido na sua API
# Verificar se o retorno, quando a tarefa já existe, é igual a {"mensagem" : "TAREFA JÁ EXISTE"} ou conforme definido na sua API

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

def test_verificar_tarefa_especifica():
    criar_tarefa_mock()
    requisicao = CLIENT.get("/tarefas/0")

    assert requisicao.status_code == 200

    dados = requisicao.json()
    assert dados["titulo"] == "tarefa_mock"
    assert dados["descricao"] == "descricao-tarefa"
    assert dados["id"] == 0
    assert dados["concluido"] == False

    requisicao = CLIENT.get("/tarefas/5")
    CLIENT.delete('/tarefas/0')

    assert requisicao.json() == {"mensagem": "Não existe nenhuma tarefa"}

def test_health():
    req = CLIENT.get("/health")

    assert req.status_code == 200
    assert req.json() == {"mensagem": "healthy"}
    
 