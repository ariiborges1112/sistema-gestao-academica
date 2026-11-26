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