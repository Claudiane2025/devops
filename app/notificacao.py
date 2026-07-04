from fastapi import FastAPI
from datetime import datetime

APP_NOTIFICACAO = FastAPI()

@APP_NOTIFICACAO.post("/notificar")
def notificar(titulo: str, data_finalizacao: datetime):
    
    print(f"Tarefa '{titulo}' finalizada em {data_finalizacao}")

    return {"status": "OK"}