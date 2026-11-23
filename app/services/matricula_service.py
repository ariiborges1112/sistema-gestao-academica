from datetime import date
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models import Curso, Disciplina, Estudante, Matricula, Professor, Turma

