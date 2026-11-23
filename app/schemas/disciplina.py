from sqlmodel import Field, SQLModel

class DisciplinaCreate(SQLModel):
    codigo: str
    nome: str 
    carga_horaria: int = Field(gt=0)
    curso_id: int

class DisciplinaUpdate(SQLModel):
    codigo: str | None = None
    nome: str | None = None
    carga_horaria: int | None = Field(default=None, gt=0)
    curso_id: int | None = None

class DisciplinaRead(SQLModel):
    id: int
    codigo: str
    nome: str 
    carga_horaria: int
    curso_id: int