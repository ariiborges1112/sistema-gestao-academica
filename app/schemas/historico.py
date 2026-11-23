from sqlmodel import SQLModel
from app.models.matricula import StatusMatricula


class ItemHistoricoRead(SQLModel):
    periodo: str
    codigo_disciplina: str
    nome_disciplina: str
    codigo_turma: str
    professor: str
    nota: float | None
    frequencia: float | None
    status: StatusMatricula


class HistoricoEstudanteRead(SQLModel):
    estudante_id: int
    nome_estudante: str
    numero_matricula: str
    curso: str
    disciplinas: list[ItemHistoricoRead]