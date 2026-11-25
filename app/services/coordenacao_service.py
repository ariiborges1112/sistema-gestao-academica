from fastapi import HTTPException
from sqlmodel import Session, select, func
from app.models import Estudante, Matricula, StatusMatricula, Turma, Disciplina, Professor
from app.schemas.coordenacao import OfertaPeriodoRead, ResultadoTurmaRead
from app.services.matricula_service import contar_vagas_ocupadas

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

def resultados_da_turma(session: Session, turma_id: int) -> ResultadoTurmaRead:
    turma = session.get(Turma, turma_id)

    if turma is None:
        raise HTTPException(status_code=404, detail="Turma não encontrada")

    disciplina = session.get(Disciplina, turma.disciplina_id)

    if disciplina is None:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")

    consulta = (
        select(Matricula.status, func.count())
        .where(Matricula.turma_id == turma_id)
        .group_by(Matricula.status)
    )

    contagem = {
        StatusMatricula.APROVADA: 0,
        StatusMatricula.REPROVADA: 0,
        StatusMatricula.CANCELADA: 0,
        StatusMatricula.ATIVA: 0
    }

    for status, total in session.exec(consulta).all():
        if status in contagem:
            contagem[status] = total

    return ResultadoTurmaRead(
        turma_id=turma.id,
        codigo_turma=turma.codigo_turma,
        periodo=turma.periodo,
        codigo_disciplina=disciplina.codigo,
        nome_disciplina=disciplina.nome,
        aprovados=contagem[StatusMatricula.APROVADA],
        reprovados=contagem[StatusMatricula.REPROVADA],
        cancelados=contagem[StatusMatricula.CANCELADA],
        ativos=contagem[StatusMatricula.ATIVA],
        total_matriculas=sum(contagem.values()),
    )

def listar_oferta_do_periodo(session: Session, periodo: str) -> list[OfertaPeriodoRead]:
    consulta = (
        select(Turma, Disciplina, Professor)
        .join(Disciplina, Disciplina.id == Turma.disciplina_id)
        .join(Professor, Professor.id == Turma.professor_id)
        .where(Turma.periodo == periodo)
        .order_by(Disciplina.codigo, Turma.codigo_turma)
    )

    linhas = session.exec(consulta).all()
    ofertas: list[OfertaPeriodoRead] = []

    for turma, disciplina, professor in linhas:
        ofertas.append(
            OfertaPeriodoRead(
                turma_id=turma.id,
                periodo=turma.periodo,
                codigo_disciplina=disciplina.codigo,
                nome_disciplina=disciplina.nome,
                codigo_turma=turma.codigo_turma,
                horario=turma.horario,
                professor=professor.nome,
                vagas_totais=turma.vagas,
                vagas_ocupadas=contar_vagas_ocupadas(session, turma.id),
            )
        )

    return ofertas

def listar_professores_da_disciplina(session: Session, disciplina_id: int) -> list[Professor]:
    disciplina = session.get(Disciplina, disciplina_id)
    if disciplina is None:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")

    consulta = (
        select(Professor)
        .join(Turma, Turma.professor_id == Professor.id)
        .where(Turma.disciplina_id == disciplina_id)
        .distinct()
        .order_by(Professor.nome)
    )

    return list(session.exec(consulta).all())

def obter_professor_da_turma(session: Session, turma_id: int) -> Professor:
    turma = session.get(Turma, turma_id)
    if turma is None:
        raise HTTPException(status_code=404, detail="Turma não encontrada")

    professor = session.get(Professor, turma.professor_id)
    if professor is None:
        raise HTTPException(status_code=404, detail="Professor não encontrado")

    return professor