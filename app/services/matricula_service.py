from datetime import date
from fastapi import HTTPException
from sqlalchemy import func
from sqlmodel import Session, select
from sqlalchemy.orm import Session
from app.models import Curso, Disciplina, Estudante, Matricula, StatusMatricula, Professor, Turma

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
    
    resultado = session.exec(consulta).one()
    return resultado.len()