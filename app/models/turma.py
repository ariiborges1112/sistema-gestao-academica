from sqlmodel import Field, SQLModel

class Turma (SQLModel, table=True):
    __tablename__ = "turma"
    id: int|None = Field(default=None, primary_key=True)
    disciplina_id: int = Field(foreign_key="disciplina.id")
    professor_id: int = Field(foreign_key="professor.id")
    periodo: str = Field(index=True)
    horario: str|None = Field(default=None)
    codigo_turma: str = Field(index=True)
    vagas: int