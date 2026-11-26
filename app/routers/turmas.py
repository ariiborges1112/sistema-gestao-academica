from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from app.database import get_session
from app.models import Disciplina, Matricula, Professor, StatusMatricula, Turma
from app.schemas.estudante import EstudanteRead
from app.schemas.turma import TurmaCreate, TurmaRead, TurmaUpdate
from app.services.coordenacao_service import listar_estudantes_da_turma
from app.services.matricula_service import contar_vagas_ocupadas, obter_vagas

router = APIRouter(prefix="/turmas", tags=["Turmas"])

def _montar_turma_read(session: Session, turma: Turma) -> TurmaRead:
    ocupadas = contar_vagas_ocupadas(session, turma.id)
    return TurmaRead(
        **turma.model_dump(),
        vagas_ocupadas=ocupadas,
        vagas_disponiveis=max(0, turma.vagas - ocupadas),
    )

@router.post("/", response_model=TurmaRead, status_code=status.HTTP_201_CREATED)
def criar_turma(dados: TurmaCreate, session: Session = Depends(get_session)):
    disciplina = session.get(Disciplina, dados.disciplina_id)
    if disciplina is None:
        raise HTTPException(status_code=404, detail="Disciplina informada não encontrada.")

    professor = session.get(Professor, dados.professor_id)
    if professor is None:
        raise HTTPException(status_code=404, detail="Professor informado não encontrado.")

    nova_turma = Turma.model_validate(dados)
    session.add(nova_turma)
    session.commit()
    session.refresh(nova_turma)
    return _montar_turma_read(session, nova_turma)

@router.get("/", response_model=list[TurmaRead])
def listar_turmas(session: Session = Depends(get_session)):
    consulta = select(Turma).order_by(Turma.periodo, Turma.codigo_turma)
    return [_montar_turma_read(session, turma) for turma in session.exec(consulta).all()]

@router.get("/{turma_id}", response_model=TurmaRead)
def buscar_turma(turma_id: int, session: Session = Depends(get_session)):
    turma = session.get(Turma, turma_id)
    if turma is None:
        raise HTTPException(status_code=404, detail="Turma não encontrada.")
    return _montar_turma_read(session, turma)

@router.put("/{turma_id}", response_model=TurmaRead)
def atualizar_turma(
    turma_id: int,
    dados: TurmaUpdate,
    session: Session = Depends(get_session),):
    turma = session.get(Turma, turma_id)
    if turma is None:
        raise HTTPException(status_code=404, detail="Turma não encontrada.")

    dados_atualizados = dados.model_dump(exclude_unset=True)

    for campo in ("disciplina_id", "professor_id", "periodo", "codigo_turma", "vagas"):
        if campo in dados_atualizados and dados_atualizados[campo] is None:
            raise HTTPException(status_code=400, detail=f"O campo {campo} não pode ser nulo.")

    if "disciplina_id" in dados_atualizados:
        disciplina = session.get(Disciplina, dados_atualizados["disciplina_id"])
        if disciplina is None:
            raise HTTPException(status_code=404, detail="Disciplina informada não encontrada.")

    if "professor_id" in dados_atualizados:
        professor = session.get(Professor, dados_atualizados["professor_id"])
        if professor is None:
            raise HTTPException(status_code=404, detail="Professor informado não encontrado.")

    if "vagas" in dados_atualizados:
        ocupadas = contar_vagas_ocupadas(session, turma_id)
        if dados_atualizados["vagas"] < ocupadas:
            raise HTTPException(
                status_code=409,
                detail="O número de vagas não pode ser menor que o de matrículas que ocupam vaga.",
            )

    for campo, valor in dados_atualizados.items():
        setattr(turma, campo, valor)
    session.add(turma)
    session.commit()
    session.refresh(turma)
    return _montar_turma_read(session, turma)

@router.delete("/{turma_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_turma(turma_id: int, session: Session = Depends(get_session)
):
    turma = session.get(Turma, turma_id)
    if turma is None:
        raise HTTPException(status_code=404, detail="Turma não encontrada.")

    matricula_vinculada = session.exec(
        select(Matricula).where(Matricula.turma_id == turma_id)
    ).first()
    if matricula_vinculada is not None:
        raise HTTPException(
            status_code=409,
            detail="Não é possível remover a turma pois existem matrículas vinculadas a ela.",
        )

    session.delete(turma)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Não é possível remover a turma pois existem registros vinculados a ela.",
        )

@router.get("/{turma_id}/estudantes", response_model=list[EstudanteRead])
def listar_estudantes_matriculados(
    turma_id: int,
    status_matricula: StatusMatricula | None = Query(default=None, alias="status"),
    session: Session = Depends(get_session),
):
    return listar_estudantes_da_turma(session, turma_id, status_matricula)

@router.get("/{turma_id}/vagas")
def consultar_vagas(turma_id: int, session: Session = Depends(get_session)):
    return obter_vagas(session, turma_id)