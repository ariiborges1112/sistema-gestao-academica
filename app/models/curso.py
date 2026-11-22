from sqlmodel import Field, SQLModel

class Curso (SQLModel, table=True):
    __tablename__ = "curso"
    id: int|None = Field(default=None, primary_key=True)
    nome: str = Field(unique=True, index=True)