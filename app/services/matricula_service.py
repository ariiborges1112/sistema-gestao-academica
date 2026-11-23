from datetime import date
from fastapi import HTTPException
from sqlmodel import Session, select, func
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

def matricular(session: Session, estudante_id: int, turma_id: int,) -> Matricula:
    estudante = session.get(Estudante, estudante_id)
    
    if not estudante:
        raise HTTPException(status_code=404, detail="Estudante não encontrado")

    turma = session.get(Turma, turma_id)

    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")

    ja_matriculado = select(Matricula).where(estudante_id, turma_id)
    session.exec(ja_matriculado).first()

    if ja_matriculado is not None:
        raise HTTPException(status_code=409, detail="Este aluno já está matriculado")

    matricula_ativa = (
        select(Matricula)
        .join(Turma, Turma.id == Matricula.turma_id)
        .where(
            Matricula.estudante_id == estudante_id,
            Turma.disciplina_id == turma.disciplina_id,
            Matricula.status == StatusMatricula.ATIVA
            )
        .first()

        is not None:
            raise HTTPException(status_code=409, detail="")
    )