import logging
import os
import time 
from app import models
from fastapi import FastAPI, Request
from app.database import create_db_and_tables

from app.routers import cursos
from app.routers import matriculas

logging.basicConfig(
    level=logging.INFO,
    format= "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger("Gestão Acadêmica")

app = FastAPI(
    title="Gestão Acadêmica",
    description="API para gestão acadêmica",
    version="1.0.0"
)

app.include_router(cursos.router)
app.include_router(matriculas.router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.middleware("http")
async def registrar_requisicoes(request: Request, call_next):
    inicio = time.perf_counter()
    
    response = await call_next(request)
    
    duracao_ms = (time.perf_counter() - inicio) * 1000 
    
    logger.info(
        "%s, %s -> %s | %.2f ms",
        request.method,
        request.url.path,
        response.status_code,
        duracao_ms
    )

    return response


#teste para saber se a API está funcionando corretamente
@app.get("/")
async def root():
    return {"message": "Bem-vindo à API de Gestão Acadêmica!"}
