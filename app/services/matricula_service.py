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

    consulta_duplicada = select(Matricula).where(
        Matricula.estudante_id == estudante_id,
        Matricula.turma_id == turma_id
    )

    ja_matriculado = session.exec(consulta_duplicada).first()    

    if ja_matriculado is not None:
        raise HTTPException(status_code=409, detail="Este aluno já está matriculado")

    consulta_ativa = (
        select(Matricula)
        .join(Turma, Turma.id == Matricula.turma_id)
        .where(
            Matricula.estudante_id == estudante_id,
            Turma.disciplina_id == turma.disciplina_id,
            Matricula.status == StatusMatricula.ATIVA
            )
        )
    matricula_ativa = session.exec(consulta_ativa).first()

    if matricula_ativa is not None:
        raise HTTPException(status_code=409, detail="O estudante ja possui matricula ativa outra turma dessa disciplina")

    vagas_ocupadas = contar_vagas_ocupadas(session, turma_id)

    if vagas_ocupadas >= turma.vagas:
        raise HTTPException(status_code=409, detail="Turma lotada")

    nova_matricula = Matricula(estudante_id=estudante_id, turma_id=turma_id)
    session.add(nova_matricula)
    session.commit()
    session.refresh(nova_matricula)
    
    return nova_matricula

def cancelar(session: Session, matricula_id: int) -> Matricula:
    matricula = session.get(Matricula, matricula_id)

    if matricula is None:
        raise HTTPException(status_code=404, detail="Matricula inexistente")

    if matricula.status != StatusMatricula.ATIVA:
        raise HTTPException(status_code=409, detail="Apenas matriculas ativas podem ser canceladas")

    matricula.status = StatusMatricula.CANCELADA
    matricula.data_cancelamento = date.today()

    session.add(matricula)
    session.commit()
    session.refresh(matricula)

    return matricula