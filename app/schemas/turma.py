from sqlmodel import Field, SQLModel

class TurmaCreate(SQLModel):
    disciplina_id: int
    professor_id: int
    periodo: str
    horario: str | None = None
    codigo_turma: str
    vagas: int = Field(gt=0)

    