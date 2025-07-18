from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid

app = FastAPI(
    title="API Tarefas EBAC",
    description="Fixando os aprendizados sobre API.",
    version="1.0.0",
    contact={
        "email" : "guilhermecedoanastacio@gmail.com",
        "name" : "Guilherme Macedo Anastacio"
    }
)

class Tarefa(BaseModel):
    nome : str
    descricao : str
    concluida : Optional[bool] = False

db_tarefas = {}
@app.get('/livros/{id_tarefa}')
@app.get("/existe")
def exibe():
    return {"Livros" : db_tarefas}


@app.post("/adiciona_tarefa")
def post_tarefa(tarefa : Tarefa):
    for id_tarefasDb in db_tarefas.keys():
        if db_tarefas[id_tarefasDb]["nome"] == tarefa.nome:
            raise HTTPException(status_code=409, detail="Tarefa ja existe!")
    id_tarefa = str(uuid.uuid4()) 
    db_tarefas[id_tarefa] = tarefa.model_dump()
    return { "msg" : "Tarefa adicionada com sucesso!", "Tarefa" : db_tarefas[id_tarefa]}
