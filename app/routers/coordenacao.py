from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.schemas.coordenacao import (
    AlocacaoProfessorRequest,
    FechamentoTurmaResponse,
    RelatorioCursoResponse,
)
from app.services import coordenacao_service

router = APIRouter(prefix="/coordenacao", tags=["Coordenação"])

@router.get("/cursos/{curso_id}/relatorio", response_model=RelatorioCursoResponse)
def obter_relatorio_curso(curso_id: int, session: Session = Depends(get_session)):
    try:
        return coordenacao_service.gerar_relatorio_curso(session, curso_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/turmas/{turma_id}/professor")
def alocar_professor_turma(
    turma_id: int,
    dados: AlocacaoProfessorRequest,
    session: Session = Depends(get_session),
):
    try:
        return coordenacao_service.alocar_professor(session, turma_id, dados.professor_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/turmas/{turma_id}/encerrar", response_model=FechamentoTurmaResponse)
def encerrar_turma(turma_id: int, session: Session = Depends(get_session)):
    try:
        return coordenacao_service.encerrar_turma(session, turma_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))