from sqlmodel import Field, SQLModel

class Estudante (SQLModel, table=True):
    __tablename__ = "estudante"
    id: int|None = Field(default=None, primary_key=True)
    nome: str = Field(index=True)
    numero_matricula: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    curso_id: int = Field(foreign_key="curso.id")