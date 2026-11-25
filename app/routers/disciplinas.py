from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.database import get_session
from app.models import Curso, Disciplina
from app.schemas.disciplina import DisciplinaCreate, DisciplinaRead, DisciplinaUpdate

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

@router.get("/", response_model=list[DisciplinaRead])
def listar_disciplinas(session: Session = Depends(get_session)):
    consulta = select(Disciplina).order_by(Disciplina.nome)
    return list(session.exec(consulta).all())

@router.get("/{disciplina_id}", response_model=DisciplinaRead)
def buscar_disciplina(disciplina_id: int, session: Session = Depends(get_session)):
    disciplina = session.get(Disciplina, disciplina_id)
    if disciplina is None:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada.")
    return disciplina

@router.put("/{disciplina_id}", response_model=DisciplinaRead)
def atualizar_disciplina(
    disciplina_id: int,
    dados: DisciplinaUpdate,
    session: Session = Depends(get_session),):
    disciplina = session.get(Disciplina, disciplina_id)
    if disciplina is None:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada.")

    dados_atualizados = dados.model_dump(exclude_unset=True)
    if "curso_id" in dados_atualizados:
        curso = session.get(Curso, dados_atualizados["curso_id"])
        if curso is None:
            raise HTTPException(status_code=404, detail="Curso informado não encontrado.")

    for campo, valor in dados_atualizados.items():
        setattr(disciplina, campo, valor)

    session.add(disciplina)
    try:
        session.commit()
        session.refresh(disciplina)
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Já existe uma disciplina cadastrada com este código.",
        )
    return disciplina
