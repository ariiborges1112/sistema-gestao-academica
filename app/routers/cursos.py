from fastapi import HTTPException, APIRouter, Depends
from sqlmodel import Session, select
from app.database import get_session
from app.models.curso import Curso
from app.schemas.curso import CursoCreate, CursoRead, CursoUpdate

router = APIRouter(prefix="/cursos", tags=["Cursos"])




