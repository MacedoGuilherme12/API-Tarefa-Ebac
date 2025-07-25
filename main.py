from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
import secrets
import uuid

from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "sqlite:///./tarefas.db"

engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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

class TarefaDB(Base):
    __tablename__ = "tarefas"  
    id = Column(Integer, primary_key=True, index=True)  
    nome = Column(String, index=True)
    descricao = Column(String, index=True)
    concluida = Column(Boolean, default=False)  

class Tarefa(BaseModel):
    nome : str
    descricao : str
    concluida : Optional[bool]

Base.metadata.create_all(bind=engine)
db_tarefas = {}

def sessao_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/tarefas/{id_tarefa}")
def get_tarefa(id_tarefa: str, db : Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(auth_user)):
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
    credentials: HTTPBasicCredentials = Depends(auth_user),
    db: Session = Depends(sessao_db)
):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Page e limit devem ser positivos.")

    start = (page - 1) * limit
    end = start + limit

    tarefas_db = db.query(TarefaDB).offset(start).limit(limit).all()
    total_tarefas = db.query(TarefaDB).count()
    

    return {
        "page": page,
        "limit": limit,
        "total": total_tarefas,
        "tarefas": [{"id" : tarefa.id, "nome" : tarefa.nome, "descrição" : tarefa.descricao, "concluida" : tarefa.concluida } for tarefa in tarefas_db]
    }

@app.post("/adiciona_tarefa")
def post_tarefa(tarefa: Tarefa, db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(auth_user)):
    nova_tarefa = TarefaDB(
        nome=tarefa.nome,
        descricao=tarefa.descricao,
        concluida=tarefa.concluida if tarefa.concluida is not None else False
    )
    db.add(nova_tarefa)
    db.commit()
    db.refresh(nova_tarefa)
    return {"message": "Tarefa adicionada com sucesso!", "id": nova_tarefa.id, "Tarefa": {
        "nome": nova_tarefa.nome,
        "descricao": nova_tarefa.descricao,
        "concluida": nova_tarefa.concluida
    }}

@app.delete('/delete/{id_tarefa}')
def deletar_tarefa(id_tarefa: int, db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(auth_user)):
    tarefa = db.query(TarefaDB).filter(TarefaDB.id == id_tarefa).first()
    if tarefa:
        db.delete(tarefa)
        db.commit()
        return {"message": "Tarefa deletada", "data": {
            "nome": tarefa.nome,
            "descricao": tarefa.descricao,
            "concluida": tarefa.concluida
        }}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada")

@app.put("/alterar/{id_tarefa}")
def alterar_tarefa(id_tarefa: int, db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(auth_user)):
    tarefa = db.query(TarefaDB).filter(TarefaDB.id == id_tarefa).first()
    if tarefa:
        tarefa.concluida = True
        db.commit()
        db.refresh(tarefa)
        return {"message": "Tarefa Finalizada", "data": {
            "nome": tarefa.nome,
            "descricao": tarefa.descricao,
            "concluida": tarefa.concluida
        }}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada")
