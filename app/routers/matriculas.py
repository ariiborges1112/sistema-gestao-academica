from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models.matricula import Matricula
from app.schemas.matricula import MatriculaCreate, MatriculaRead, MatriculaUpdate
from app.services import matricula_service

router = APIRouter(prefix="/matriculas", tags=["Matricula"])

@router.post("/", response_model=MatriculaRead, status_code=201)
def realizar_matricula(dados: MatriculaCreate, session: Session = Depends(get_session)):
    try:
        return matricula_service.matricular_estudante(session, dados)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))