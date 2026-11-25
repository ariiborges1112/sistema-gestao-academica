from fastapi import APIRouter
from sqlmodel import Session

from app.models import Turma
from app.schemas.turma import TurmaRead
from app.services.matricula_service import contar_vagas_ocupadas

router = APIRouter(prefix="/turmas", tags=["Turmas"])


def _montar_turma_read(session: Session, turma: Turma) -> TurmaRead:
    ocupadas = contar_vagas_ocupadas(session, turma.id)
    return TurmaRead(
        **turma.model_dump(),
        vagas_ocupadas=ocupadas,
        vagas_disponiveis=max(0, turma.vagas - ocupadas),
    )