from datetime import date
from fastapi import HTTPException
from sqlmodel import Session, select, func
from sqlalchemy.exc import IntegrityError
from app.models import Estudante, Matricula, StatusMatricula, Turma

STATUS_QUE_OCUPAM_VAGA = (
    StatusMatricula.ATIVA, 
    StatusMatricula.APROVADA, 
    StatusMatricula.REPROVADA
    )
NOTA_MINIMA = 7.0
FREQUENCIA_MINIMA = 75.0 # em percentual

def _tentar_buscar_matricula(session: Session, matricula_id: int) -> Matricula:
    matricula = session.get(Matricula, matricula_id)
    
    if matricula is None:
        raise HTTPException(status_code=404, detail="Matrícula inexistente")

    return matricula

def _confirmar_transacao(session: Session) -> None:
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Conflito de integridade no banco de dados (registro duplicado ou invalido)")
    except Exception:
        session.rollback()
        raise

def contar_vagas_ocupadas(session: Session, turma_id: int) -> int:
    consulta = (
        select(func.count())
        .select_from(Matricula)
        .where(
            Matricula.turma_id == turma_id, 
            Matricula.status.in_(STATUS_QUE_OCUPAM_VAGA)
        )
    )
    
    total = session.exec(consulta).one()
    return total

def matricular(session: Session, estudante_id: int, turma_id: int,) -> Matricula:
    estudante = session.get(Estudante, estudante_id)
    
    if estudante is None:
        raise HTTPException(status_code=404, detail="Estudante não encontrado")
 
    turma = session.get(Turma, turma_id)

    if turma is None:
        raise HTTPException(status_code=404, detail="Turma não encontrada")

    consulta_duplicada = select(Matricula).where(
        Matricula.estudante_id == estudante_id,
        Matricula.turma_id == turma_id
    )

    ja_matriculado = session.exec(consulta_duplicada).first()    

    if ja_matriculado is not None:
        raise HTTPException(status_code=409, detail="Este aluno já está matriculado")

    consulta_ativa = (
        select(Matricula)
        .join(Turma, Turma.id == Matricula.turma_id)
        .where(
            Matricula.estudante_id == estudante_id,
            Turma.disciplina_id == turma.disciplina_id,
            Matricula.status == StatusMatricula.ATIVA
            )
        )
    matricula_ativa = session.exec(consulta_ativa).first()

    if matricula_ativa is not None:
        raise HTTPException(status_code=409, detail="O estudante ja possui matricula ativa outra turma dessa disciplina")

    vagas_ocupadas = contar_vagas_ocupadas(session, turma_id)

    if vagas_ocupadas >= turma.vagas:
        raise HTTPException(status_code=409, detail="Turma lotada")

    nova_matricula = Matricula(estudante_id=estudante_id, turma_id=turma_id)

    session.add(nova_matricula)
    _confirmar_transacao(session)
    session.refresh(nova_matricula)
    
    return nova_matricula

def cancelar_matricula(session: Session, matricula_id: int) -> Matricula:
    matricula = _tentar_buscar_matricula(session, matricula_id)

    if matricula.status != StatusMatricula.ATIVA:
        raise HTTPException(status_code=409, detail="Apenas matriculas ativas podem ser canceladas")

    matricula.status = StatusMatricula.CANCELADA
    matricula.data_cancelamento = date.today()

    session.add(matricula)
    _confirmar_transacao(session)
    session.refresh(matricula)

    return matricula

def lancar_desempenho(session: Session, matricula_id: int, nota: float | None, 
                      frequencia: float | None) -> Matricula:
    if nota is None and frequencia is None:
        raise HTTPException(status_code=400, detail="Nota ou frequencia não passadas")
    
    matricula = _tentar_buscar_matricula(session, matricula_id)

    if matricula.status != StatusMatricula.ATIVA:
        raise HTTPException(status_code=409, detail="Apenas matriculas ativas podem ter notas e frequencia lançadas")
    
    if nota is not None:
        if nota < 0.0 or nota > 10.0:
            raise HTTPException(status_code=400, detail="A nota deve estar entre 0 e 10")
        
        matricula.nota = nota

    if frequencia is not None:
        if frequencia < 0.0 or frequencia > 100.0:
            raise HTTPException(status_code=400, detail="A frequencia deve estar entre 0 e 100%")
        
        matricula.frequencia = frequencia

    session.add(matricula)
    _confirmar_transacao(session)
    session.refresh(matricula)

    return matricula

def encerrar_matricula(session: Session, matricula_id: int) -> Matricula:
    matricula = _tentar_buscar_matricula(session, matricula_id)
    
    if matricula.status != StatusMatricula.ATIVA:
        raise HTTPException(status_code=409, detail="Apenas matriculas ativas podem ser encerradas")

    if matricula.nota is None or matricula.frequencia is None:
        raise HTTPException(status_code=400, detail="A nota ou/e a frequencia ainda não foram lançadas")

    if matricula.nota >= NOTA_MINIMA and matricula.frequencia >= FREQUENCIA_MINIMA:
        matricula.status = StatusMatricula.APROVADA
    else:
        matricula.status = StatusMatricula.REPROVADA

    session.add(matricula)
    _confirmar_transacao(session)
    session.refresh(matricula)

    return matricula

def buscar_matricula(session: Session, matricula_id: int) -> Matricula:
    return _tentar_buscar_matricula(session, matricula_id)

def obter_vagas(session: Session, turma_id: int) -> dict:
    turma = session.get(Turma, turma_id)

    if turma is None:
        raise HTTPException(status_code=404, detail="Turma não encontrada")

    ocupadas = contar_vagas_ocupadas(session, turma_id)

    disponiveis = max(0, turma.vagas - ocupadas)

    return{
        "vagas": turma.vagas,
        "vagas_ocupadas": ocupadas,
        "vagas_disponiveis": disponiveis
    }

def listar_matriculas(session: Session, estudante_id: int | None = None,
                      turma_id: int | None = None, periodo: str | None = None,
                      status: StatusMatricula | None = None, limite: int = 50,
                      deslocamento: int = 0) -> list[Matricula]:
    if limite < 1 or limite > 100:
        raise HTTPException(status_code=400, detail="O limite deve estar entre 1 e 100")

    if deslocamento < 0:
        raise HTTPException(status_code=400, detail="O deslocamento não pode ser negativo")

    consulta = select(Matricula)
    
    if estudante_id is not None:
        consulta = consulta.where(Matricula.estudante_id == estudante_id)

    if turma_id is not None:
        consulta = consulta.where(Matricula.turma_id == turma_id)

    if status is not None:
        consulta = consulta.where(Matricula.status == status)

    if periodo is not None:
        consulta = consulta.join(Turma, Turma.id == Matricula.turma_id).where(
            Turma.periodo == periodo
        )

    consulta = consulta.order_by(Matricula.id).offset(deslocamento).limit(limite)

    return list(session.exec(consulta).all())