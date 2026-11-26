from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.database import get_session
from app.models import Curso, Estudante, Matricula
from app.schemas.estudante import EstudanteCreate, EstudanteRead, EstudanteUpdate
from app.schemas.historico import HistoricoEstudanteRead
from app.services.historico_service import gerar_historico

router = APIRouter(prefix="/estudantes", tags=["Estudantes"])


@router.post("/", response_model=EstudanteRead, status_code=status.HTTP_201_CREATED)
def criar_estudante(dados: EstudanteCreate, session: Session = Depends(get_session)):
    if session.get(Curso, dados.curso_id) is None:
        raise HTTPException(status_code=404, detail="Curso informado não encontrado")

    novo_estudante = Estudante.model_validate(dados)
    session.add(novo_estudante)
    try:
        session.commit()
        session.refresh(novo_estudante)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Já existe um estudante com este número de matrícula ou e-mail")
    return novo_estudante


@router.get("/", response_model=list[EstudanteRead])
def listar_estudantes(session: Session = Depends(get_session)):
    consulta = select(Estudante).order_by(Estudante.nome)
    return list(session.exec(consulta).all())


@router.get("/{estudante_id}", response_model=EstudanteRead)
def buscar_estudante(estudante_id: int, session: Session = Depends(get_session)):
    estudante = session.get(Estudante, estudante_id)
    if estudante is None:
        raise HTTPException(status_code=404, detail="Estudante não encontrado")
    return estudante


@router.put("/{estudante_id}", response_model=EstudanteRead)
def atualizar_estudante(
    estudante_id: int,
    dados: EstudanteUpdate,
    session: Session = Depends(get_session),
):
    estudante = session.get(Estudante, estudante_id)
    if estudante is None:
        raise HTTPException(status_code=404, detail="Estudante não encontrado")

    dados_brutos = dados.model_dump(exclude_unset=True)
    if any(valor is None for valor in dados_brutos.values()):
        raise HTTPException(
            status_code=422,
            detail="Campos obrigatórios não podem ser atualizados para null",
        )
    
    if "curso_id" in dados_brutos:
        curso = session.get(Curso, dados_brutos["curso_id"])
        if curso is None:
            raise HTTPException(status_code=404, detail="Curso informado não encontrado")

    for campo, valor in dados_brutos.items():
        setattr(estudante, campo, valor)

    session.add(estudante)
    try:
        session.commit()
        session.refresh(estudante)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Já existe um estudante com este número de matrícula ou e-mail")
    return estudante


@router.delete("/{estudante_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_estudante(estudante_id: int, session: Session = Depends(get_session)):
    estudante = session.get(Estudante, estudante_id)
    if estudante is None:
        raise HTTPException(status_code=404, detail="Estudante não encontrado")

    session.delete(estudante)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Não é possível remover o estudante pois existem matrículas vinculadas a ele")


@router.get("/{estudante_id}/historico", response_model=HistoricoEstudanteRead)
def consultar_historico(estudante_id: int, session: Session = Depends(get_session)):
    return gerar_historico(session, estudante_id)