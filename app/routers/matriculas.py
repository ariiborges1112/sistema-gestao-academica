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


@router.get("/", response_model=list[MatriculaRead])
def listar_matriculas(session: Session = Depends(get_session)):
    return session.exec(select(Matricula)).all()


@router.get("/{matricula_id}", response_model=MatriculaRead)
def buscar_matricula(matricula_id: int, session: Session = Depends(get_session)):
    matricula = session.get(Matricula, matricula_id)
    if matricula is None:
        raise HTTPException(status_code=404, detail="Matricula não encontrada")
    return matricula


@router.patch("/{matricula_id}", response_model=MatriculaRead)
def atualizar_matricula(matricula_id: int, dados: MatriculaUpdate, session: Session = Depends(get_session)):
    try: 
        return matricula_service.atualizar_matricula(session, matricula_id, dados)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


