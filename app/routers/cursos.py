from fastapi import HTTPException, APIRouter, Depends
from sqlmodel import Session, select
from app.database import get_session
from app.models.curso import Curso
from app.schemas.curso import CursoCreate, CursoRead, CursoUpdate

router = APIRouter(prefix="/cursos", tags=["Cursos"])

@router.post("/", response_model=CursoRead, status_code=201)
def criar_curso(dados: CursoCreate, session: Session = Depends(get_session)):
    if session.exec(select(Curso).where(Curso.nome == dados.nome)).first():
        raise HTTPException(status_code=400, detail="Curso já existe")
    novo_curso = Curso.model_validate(dados)
    session.add(novo_curso)
    session.commit()
    session.refresh(novo_curso)
    return novo_curso

@router.get("/", response_model=list[CursoRead])
def listar_cursos(session: Session = Depends(get_session)):
    cursos = session.exec(select(Curso)).all()
    return cursos

@router.get("/{curso_id}", response_model=CursoRead)
def buscar_curso(curso_id: int, session: Session = Depends(get_session)):
    curso = session.get(Curso, curso_id)
    if curso is None:
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    return curso






