"""
Exercise 01 — Node Registry API

Implement a FastAPI application with the following endpoints:

GET    /health          → health check with DB status
POST   /api/nodes       → register a new node
GET    /api/nodes       → list all nodes
GET    /api/nodes/{name} → get a node by name
PUT    /api/nodes/{name} → update a node
DELETE /api/nodes/{name} → soft-delete a node (set status=inactive)

See README.md for full specification.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Response
from .database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import Node
from .schemas import NodeCreate, NodeUpdate
from src.database import Base, engine
import src.models

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

app = FastAPI()
@app.get("/health")
def estado(db: Session = Depends(get_db)):
    activos = db.query(func.count(Node.id)).filter(Node.status == "active").scalar()
    return {
        "status": "ok",
        "db": "connected",
        "nodes_count": activos
    }

@app.post("/api/nodes",status_code=status.HTTP_201_CREATED)
def registrar_nodo(node: NodeCreate, db: Session = Depends(get_db)):
    nodo_existente = db.query(Node).filter(Node.name == node.name).first()
    if nodo_existente:
        raise HTTPException(status_code=409,detail="Node already exists")
    nuevo = Node(
        name=node.name,
        host=node.host,
        port=node.port
    )
    
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@app.get("/api/nodes")
def lista_nodos(db: Session = Depends(get_db)):
    return db.query(Node).all()

@app.get("/api/nodes/{name}")
def obtener_nodo(name: str, db: Session = Depends(get_db)):
    nodo = db.query(Node).filter(Node.name == name).first()
    if not nodo: 
        raise HTTPException(status_code=404,detail="Node not found")
    return nodo

@app.put("/api/nodes/{name}")
def actualizar_nodo(name: str, data: NodeUpdate, db: Session = Depends(get_db)):
    nodo = db.query(Node).filter(Node.name == name).first()
    if not nodo:
        raise HTTPException(status_code=404,detail="Node not found")
    if data.host is not None:
        nodo.host = data.host
    if data.port is not None:
        nodo.port = data.port
    if data.status is not None:
        nodo.status = data.status

    db.commit()
    db.refresh(nodo)

    return nodo

@app.delete("/api/nodes/{name}", status_code=status.HTTP_204_NO_CONTENT)
def desactivar_nodo(name: str, data: NodeUpdate, db: Session = Depends(get_db)):
    nodo = db.query(Node).filter(Node.name == name).first()
    if not nodo:
        raise HTTPException(status_code=404,detail="Node not found")
    nodo.status = "inactive"
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

