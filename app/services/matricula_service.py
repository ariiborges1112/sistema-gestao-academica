from datetime import date
from fastapi import HTTPException
from sqlalchemy import func
from sqlmodel import Session, select
from app.models import Estudante, Matricula, StatusMatricula, Turma

STATUS_QUE_OCUPAM_VAGA = (
    StatusMatricula.ATIVA, 
    StatusMatricula.APROVADA, 
    StatusMatricula.REPROVADA
    )
NOTA_MINIMA = 7.0
FREQUENCIA_MINIMA = 75.0 # em percentual

def contar_vagas_ocupadas(session: Session, turma_id: int) -> int:
    consulta = (
        select(func.count())
        .select_from(Matricula)
        .where(
            Matricula.turma_id == turma_id, 
            Matricula.status.in_(STATUS_QUE_OCUPAM_VAGA)
        )
    )
    
    total = session.exec(consulta).one()
    return total

def matricular():
    