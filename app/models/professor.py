from sqlmodel import Field, SQLModel

class Professor (SQLModel, table=True):
    __tablename__ = "professor"
    id: int|None = Field(default=None, primary_key=True)
    nome: str = Field(index=True)
    email: str = Field(unique=True, index=True)