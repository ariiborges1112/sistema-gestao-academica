from fastapi import HTTPException
from sqlmodel import Session, select
from app.models import Curso, Disciplina, Estudante, Matricula, Professor, Turma
from app.schemas.historico import HistoricoEstudanteRead, ItemHistoricoRead

def gerar_historico(session: Session, estudante_id: int) -> HistoricoEstudanteRead:
    estudante = session.get(Estudante, estudante_id)

    if estudante is None:
        raise HTTPException(status_code=404, detail="Estudante não encontrado")

    curso = session.get(Curso, estudante.curso_id)

    if curso is None:
        raise HTTPException(status_code=404, detail="Curso do estudante não encontrado")

    consulta = (
        select(Matricula, Turma, Disciplina, Professor)
        .join(Turma, Turma.id == Matricula.turma_id)
        .join(Disciplina, Disciplina.id == Turma.disciplina_id)
        .join(Professor, Professor.id == Turma.professor_id)
        .where(Matricula.estudante_id == estudante_id)
        .order_by(Turma.periodo, Disciplina.codigo, Matricula.id)
    )

    linhas = session.exec(consulta).all()

    itens: list[ItemHistoricoRead] = []

    for matricula, turma, disciplina, professor in linhas:
        itens.append(
            ItemHistoricoRead(
                periodo=turma.periodo,
                codigo_disciplina=disciplina.codigo,
                nome_disciplina=disciplina.nome,
                codigo_turma=turma.codigo_turma,
                professor=professor.nome,
                nota=matricula.nota,
                frequencia=matricula.frequencia,
                status=matricula.status,
            )
        )

    return HistoricoEstudanteRead(
        estudante_id=estudante.id, 
        nome_estudante=estudante.nome, 
        numero_matricula=estudante.numero_matricula, 
        curso=curso.nome, 
        disciplinas=itens
    )