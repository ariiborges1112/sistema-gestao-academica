from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.database import get_session
from app.models import Professor
from app.schemas.professor import ProfessorCreate, ProfessorRead, ProfessorUpdate

router = APIRouter(prefix="/professores", tags=["Professores"])

@router.post("/", response_model=ProfessorRead, status_code=status.HTTP_201_CREATED)
def criar_professor(dados: ProfessorCreate, session: Session = Depends(get_session)):
    novo_professor = Professor.model_validate(dados)
    session.add(novo_professor)
    try:
        session.commit()
        session.refresh(novo_professor)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Já existe um professor cadastrado com este e-mail.")
    return novo_professor


@router.get("/", response_model=list[ProfessorRead])
def listar_professores(session: Session = Depends(get_session)):
    consulta = select(Professor).order_by(Professor.nome)
    return list(session.exec(consulta).all())


@router.get("/{professor_id}", response_model=ProfessorRead)
def buscar_professor(professor_id: int, session: Session = Depends(get_session)):
    professor = session.get(Professor, professor_id)
    if professor is None:
        raise HTTPException(status_code=404, detail="Professor não encontrado.")
    return professor


@router.put("/{professor_id}", response_model=ProfessorRead)
def atualizar_professor(
    professor_id: int,
    dados: ProfessorUpdate,
    session: Session = Depends(get_session),
):
    professor = session.get(Professor, professor_id)
    if professor is None:
        raise HTTPException(status_code=404, detail="Professor não encontrado.")

    dados_atualizados = dados.model_dump(exclude_unset=True)
    for campo, valor in dados_atualizados.items():
        setattr(professor, campo, valor)

    session.add(professor)
    try:
        session.commit()
        session.refresh(professor)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Já existe um professor cadastrado com este e-mail.")
    return professor


@router.delete("/{professor_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_professor(professor_id: int, session: Session = Depends(get_session)):
    professor = session.get(Professor, professor_id)
    if professor is None:
        raise HTTPException(status_code=404, detail="Professor não encontrado.")

    session.delete(professor)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Não é possível remover o professor pois existem turmas vinculadas a ele.",
        )