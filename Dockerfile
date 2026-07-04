FROM python:3.12-slim

RUN mkdir app/

WORKDIR app/

COPY requirements.txt .
COPY app/main.py .
COPY app/notificacao.py .

RUN pip install -r requirements.txt

ENTRYPOINT ["fastapi", "run"]