from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.database import get_session
from app.models import Curso, Disciplina
from app.schemas.disciplina import DisciplinaCreate, DisciplinaRead

router = APIRouter(prefix="/disciplinas", tags=["Disciplinas"])


@router.post("/", response_model=DisciplinaRead, status_code=status.HTTP_201_CREATED)
def criar_disciplina(dados: DisciplinaCreate, session: Session = Depends(get_session)):
    curso = session.get(Curso, dados.curso_id)
    if curso is None:
        raise HTTPException(status_code=404, detail="Curso informado não encontrado.")

    nova_disciplina = Disciplina.model_validate(dados)
    session.add(nova_disciplina)
    try:
        session.commit()
        session.refresh(nova_disciplina)
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Já existe uma disciplina cadastrada com este código.",
        )
    return nova_disciplina