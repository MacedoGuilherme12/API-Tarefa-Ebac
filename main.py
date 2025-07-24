from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
import secrets
import uuid

meu_usuario = "admin"
minha_senha="admin"
security = HTTPBasic()

app = FastAPI(
    title="API Tarefas EBAC",
    description="Fixando os aprendizados sobre API.",
    version="1.0.0",
    contact={
        "email" : "guilhermecedoanastacio@gmail.com",
        "name" : "Guilherme Macedo Anastacio"
    }
)
def auth_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    is_username_corretc = secrets.compare_digest(credentials.username, meu_usuario)
    is_password_corretc = secrets.compare_digest(credentials.password, minha_senha)
    if not (is_password_corretc and is_username_corretc):
        raise HTTPException(
            status_code=401,
            detail="Usuario e Senha incorretos",
            headers={"WWW-Authenticate" : "Basic"}
        )
class Tarefa(BaseModel):
    nome : str
    descricao : str
    concluida : Optional[bool] = False

db_tarefas = {}

@app.get("/tarefas/{id_tarefa}")
def getTarefa(id_tarefa: str):
    if id_tarefa in db_tarefas:
        return {"data": list(db_tarefas[id_tarefa])}
    raise HTTPException(status_code=409,detail="Essa tarefa não existe!")
        

@app.get("/tarefas")
def getTarefas(page: int = 1, limit: int = 10, credentials: HTTPBasicCredentials = Depends(security)):
    is_username_correct = secrets.compare_digest(credentials.username, meu_usuario)
    is_password_correct = secrets.compare_digest(credentials.password, minha_senha)
    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=401,
            detail="Usuario e Senha incorretos",
            headers={"WWW-Authenticate": "Basic"}
        )

    if not db_tarefas:
        raise HTTPException(status_code=404, detail="Não existe tarefas!!")

    start = (page - 1) * limit
    end = start + limit

    lista_ordenada = sorted(db_tarefas.items(), key=lambda x : x[0])
    tarefas_paginadas = [
        {"id": id_tarefa, "nome": tarefa.nome, "descricao": tarefa.descricao, "concluida": tarefa.concluida}
        for id_tarefa, tarefa in lista_ordenada[start:end]
    ]
    
    return {
        "page": page,
        "limit": limit,
        "total": len(db_tarefas),
        "tarefas": tarefas_paginadas
    }


@app.post("/adiciona_tarefa")
def post_tarefa(tarefa : Tarefa):
    
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
    raise HTTPException(status_code=404, detail="Tarefa não encontrada")