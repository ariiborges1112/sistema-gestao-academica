from datetime import date
from enum import Enum
from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field


class StatusMatricula(str, Enum):
    ATIVA = "ATIVA"
    CANCELADA = "CANCELADA"
    CONCLUIDA = "CONCLUIDA"
    APROVADA = "APROVADA"
    REPROVADA = "REPROVADA"


class Matricula(SQLModel, table=True):
    __tablename__ = "matricula"
    __table_args__ = (UniqueConstraint("estudante_id", "turma_id", name="uq_matricula_estudante_turma"),)
    id: int | None = Field(default=None, primary_key=True)
    estudante_id: int = Field(foreign_key="estudante.id", index=True)
    turma_id: int = Field(foreign_key="turma.id", index=True)
    status: StatusMatricula = Field(default=StatusMatricula.ATIVA)
    nota: float | None = Field(default=None)
    frequencia: float | None = Field(default=None)
    data_matricula: date = Field(default_factory=date.today)
    data_cancelamento: date | None = Field(default=None)