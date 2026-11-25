from fastapi import HTTPException
from sqlmodel import Session, select, func
from app.models import Estudante, Matricula, StatusMatricula, Turma, Disciplina, Professor
from app.schemas.coordenacao import OfertaPeriodoRead, ResultadoTurmaRead

def listar_estudantes_da_turma(session: Session, turma_id: int, 
                               status: StatusMatricula | None = None) -> list[Estudante]:
    turma = session.get(Turma, turma_id)

    if turma is None:
        raise HTTPException(status_code=404, detail="Turma não encontrada")

    consulta = (
        select(Estudante)
        .join(Matricula, Matricula.estudante_id == Estudante.id)
        .where(Matricula.turma_id == turma_id)
    )

    if status is not None:
        consulta = consulta.where(Matricula.status == status)

    consulta = consulta.order_by(Estudante.nome)

    return list(session.exec(consulta).all())

#def resultados_da_turma(session: Session, turma_id: int) -> ResultadoTurmaRead:
    turma = session.get(Turma, turma_id)

    if turma is None:
        raise HTTPException(status_code=404, detail="Turma não encontrada")

    consulta = (
        select(Matricula.status),
        func.count()
        .where(Matricula.turma_id == turma_id)
        .group_by(Matricula.status)
    )

    status = []