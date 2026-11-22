from sqlmodel import Field, SQLModel

class Disciplina (SQLModel, table=True):
    __tablename__ = "disciplina"
    id: int|None = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True, index=True)
    nome: str = Field(index=True)
    carga_horaria: int 
    curso_id: int = Field(foreign_key="curso.id")