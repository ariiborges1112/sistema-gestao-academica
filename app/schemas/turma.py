from sqlmodel import Field, SQLModel

class TurmaCreate(SQLModel):
    disciplina_id: int
    professor_id: int
    periodo: str
    horario: str | None = None
    codigo_turma: str
    vagas: int = Field(gt=0)

class TurmaUpdate(SQLModel):
    disciplina_id: int | None = None
    professor_id: int | None = None
    periodo: str | None = None
    horario: str | None = None
    codigo_turma: str | None = None
    vagas: int | None = Field(default=None, gt=0)

class TurmaRead(SQLModel):
    id: int
    disciplina_id: int
    professor_id: int
    periodo: str
    horario: str | None = None
    codigo_turma: str
    vagas: int 
    vagas_ocupadas: int = 0
    vagas_disponiveis: int = 0

