from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_session
from app.models import Disciplina, Professor, Turma
from app.schemas.turma import TurmaCreate, TurmaRead
from app.services.matricula_service import contar_vagas_ocupadas

router = APIRouter(prefix="/turmas", tags=["Turmas"])


def _montar_turma_read(session: Session, turma: Turma) -> TurmaRead:
    ocupadas = contar_vagas_ocupadas(session, turma.id)
    return TurmaRead(
        **turma.model_dump(),
        vagas_ocupadas=ocupadas,
        vagas_disponiveis=max(0, turma.vagas - ocupadas),
    )

@router.post("/", response_model=TurmaRead, status_code=status.HTTP_201_CREATED)
def criar_turma(dados: TurmaCreate, session: Session = Depends(get_session)):
    disciplina = session.get(Disciplina, dados.disciplina_id)
    if disciplina is None:
        raise HTTPException(status_code=404, detail="Disciplina informada não encontrada.")

    professor = session.get(Professor, dados.professor_id)
    if professor is None:
        raise HTTPException(status_code=404, detail="Professor informado não encontrado.")

    nova_turma = Turma.model_validate(dados)
    session.add(nova_turma)
    session.commit()
    session.refresh(nova_turma)
    return _montar_turma_read(session, nova_turma)