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

@app.get("/tarefas/{id_tarefa}")
def getTarefa(id_tarefa: int):
    if id_tarefa in db_tarefas:
        return {"data": db_tarefas[id_tarefa]}
    raise HTTPException(status_code=409,detail="Essa tarefa não existe!")
        

@app.get("/tarefas")
def getTarefas():
    return {"Tarefas" : db_tarefas}


@app.post("/adiciona_tarefa")
def post_tarefa(tarefa : Tarefa):
    for id_tarefasDb in db_tarefas.keys():
        if db_tarefas[id_tarefasDb].nome == tarefa.nome:
            raise HTTPException(status_code=409, detail="Tarefa ja existe!")
    id_tarefa = str(uuid.uuid4()) 
    db_tarefas[id_tarefa] = tarefa
    return { "message" : "Tarefa adicionada com sucesso!", "id" : id_tarefa, "Tarefa" : db_tarefas[id_tarefa]}

@app.delete('/delete/{nome}')
def deletar_tarefa(nome : str):
    for id_tarefa, tarefa in db_tarefas.items():
        if nome == tarefa.nome :
            tarefa_deletada = db_tarefas.pop(id_tarefa)
            return {"message" : "Tarefa deletada", "data" : tarefa_deletada}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada")

@app.put("/alterar/{nome}")
def alterar_tarefa(nome : str):
    for id_tarefa, tarefa in db_tarefas.items():
        if nome == tarefa.nome :
            db_tarefas[id_tarefa].concluida = True
            return {"message" : "Tarefa Finalizada", "data" : db_tarefas[id_tarefa]}
    return {"teste" : "sim"}