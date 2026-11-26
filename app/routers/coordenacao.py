from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.database import get_session
from app.models import Estudante, Professor, StatusMatricula
from app.schemas.coordenacao import OfertaPeriodoRead, ResultadoTurmaRead
from app.schemas.estudante import EstudanteRead
from app.schemas.professor import ProfessorRead
from app.services import coordenacao_service

router = APIRouter(prefix="/coordenacao", tags=["Coordenação"])


@router.get("/turmas/{turma_id}/estudantes", response_model=list[EstudanteRead])
def consultar_estudantes_turma(
    turma_id: int,
    status: StatusMatricula | None = Query(default=None),
    session: Session = Depends(get_session),
) -> list[Estudante]:
    return coordenacao_service.listar_estudantes_da_turma(session, turma_id, status)


@router.get("/ofertas", response_model=list[OfertaPeriodoRead])
def consultar_oferta_periodo(
    periodo: str = Query(..., min_length=1),
    session: Session = Depends(get_session),
) -> list[OfertaPeriodoRead]:
    return coordenacao_service.listar_oferta_do_periodo(session, periodo)


@router.get("/disciplinas/{disciplina_id}/professores", response_model=list[ProfessorRead])
def consultar_professores_disciplina(
    disciplina_id: int,
    session: Session = Depends(get_session),
) -> list[Professor]:
    return coordenacao_service.listar_professores_da_disciplina(session, disciplina_id)


@router.get("/turmas/{turma_id}/professor", response_model=ProfessorRead)
def consultar_professor_turma(
    turma_id: int,
    session: Session = Depends(get_session),
) -> Professor:
    return coordenacao_service.obter_professor_da_turma(session, turma_id)


@router.get("/turmas/{turma_id}/resultados", response_model=ResultadoTurmaRead)
def consultar_resultados_turma(
    turma_id: int,
    session: Session = Depends(get_session),
) -> ResultadoTurmaRead:
    return coordenacao_service.resultados_da_turma(session, turma_id)