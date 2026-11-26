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