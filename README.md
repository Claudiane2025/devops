# API DevOps - Gerenciamento de Tarefas

Repositório:
https://github.com/Claudiane2025/devops

## Descrição da aplicação

Esta aplicação é uma API REST desenvolvida em Python utilizando o framework FastAPI.

A API disponibiliza recursos para gerenciamento de tarefas, permitindo:

- Criar tarefas;
- Listar todas as tarefas;
- Consultar uma tarefa específica;
- Atualizar tarefas;
- Remover tarefas.

A aplicação possui documentação automática utilizando Swagger/OpenAPI, disponível através do endpoint `/docs`.

Também possui endpoints de monitoramento:

- `/health` - verificação de saúde da aplicação;
- `/metricas` - informações de métricas da aplicação.

O projeto foi estruturado seguindo práticas DevOps, utilizando:

- Containerização com Docker;
- Orquestração com Kubernetes;
- Pipeline CI/CD utilizando GitHub Actions;
- Análise de qualidade e segurança do código.

---
## Tecnologias utilizadas

* Python
* FastAPI
* Docker
* Kubernetes (Minikube)
* Git
* GitHub
* GitHub Actions
* YAML
* OpenAPI (Swagger)

---
## Execução local

1. Clonar o repositório.
2. Criar um ambiente virtual Python.
3. Instalar as dependências utilizando:

```bash
pip install -r requirements.txt
```

3. Aplicar os manifestos kubernetes:

```bash
kubectl apply -f deployment.yaml
```
4. Verificar os pods:

```bash
kubectl get pods
```
5. Acessar a aplicação usando o port-forward
```bash
kubectl port-forward svc/devops-svc 8000:8000
```

6. Acessar:
```
http://localhost:8000/docs
```
