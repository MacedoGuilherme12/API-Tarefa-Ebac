from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
import secrets
import uuid

meu_usuario = "admin"
minha_senha = "admin"
security = HTTPBasic()

app = FastAPI(
    title="API Tarefas EBAC",
    description="Fixando os aprendizados sobre API.",
    version="1.0.0",
    contact={
        "email": "guilhermecedoanastacio@gmail.com",
        "name": "Guilherme Macedo Anastacio"
    }
)

def auth_user(credentials: HTTPBasicCredentials = Depends(security)):
    is_username_correct = secrets.compare_digest(credentials.username, meu_usuario)
    is_password_correct = secrets.compare_digest(credentials.password, minha_senha)
    if not (is_password_correct and is_username_correct):
        raise HTTPException(
            status_code=401,
            detail="Usuario e Senha incorretos",
            headers={"WWW-Authenticate": "Basic"}
        )

class Tarefa(BaseModel):
    nome: str
    descricao: str
    concluida: Optional[bool] = False

db_tarefas = {}

@app.get("/tarefas/{id_tarefa}")
def get_tarefa(id_tarefa: str, credentials: HTTPBasicCredentials = Depends(auth_user)):
    if id_tarefa in db_tarefas:
        tarefa = db_tarefas[id_tarefa]
        return {
            "id": id_tarefa,
            "nome": tarefa.nome,
            "descricao": tarefa.descricao,
            "concluida": tarefa.concluida
        }
    raise HTTPException(status_code=404, detail="Essa tarefa não existe!")

@app.get("/tarefas")
def get_tarefas(
    page: int = 1,
    limit: int = 10,
    order_by: Optional[str] = "id",
    credentials: HTTPBasicCredentials = Depends(auth_user)
):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Page e limit devem ser positivos.")

    if not db_tarefas:
        raise HTTPException(status_code=404, detail="Não existe tarefas!!")

    valid_order_fields = {"id", "nome", "descricao", "concluida"}
    if order_by not in valid_order_fields:
        raise HTTPException(status_code=400, detail=f"order_by deve ser um dos: {', '.join(valid_order_fields)}")

    if order_by == "id":
        lista_ordenada = sorted(db_tarefas.items(), key=lambda x: x[0])
    else:
        lista_ordenada = sorted(db_tarefas.items(), key=lambda x: getattr(x[1], order_by))

    start = (page - 1) * limit
    end = start + limit
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
def post_tarefa(tarefa: Tarefa, credentials: HTTPBasicCredentials = Depends(auth_user)):
    id_tarefa = str(uuid.uuid4())
    db_tarefas[id_tarefa] = tarefa
    return {"message": "Tarefa adicionada com sucesso!", "id": id_tarefa, "Tarefa": db_tarefas[id_tarefa]}

@app.delete('/delete/{id_tarefa}')
def deletar_tarefa(id_tarefa: str, credentials: HTTPBasicCredentials = Depends(auth_user)):
    if id_tarefa in db_tarefas:
        tarefa_deletada = db_tarefas.pop(id_tarefa)
        return {"message": "Tarefa deletada", "data": tarefa_deletada}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada")

@app.put("/alterar/{id_tarefa}")
def alterar_tarefa(id_tarefa: str, credentials: HTTPBasicCredentials = Depends(auth_user)):
    if id_tarefa in db_tarefas:
        db_tarefas[id_tarefa].concluida = True
        return {"message": "Tarefa Finalizada", "data": db_tarefas[id_tarefa]}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada")
