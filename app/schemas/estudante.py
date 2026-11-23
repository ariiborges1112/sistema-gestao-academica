from sqlmodel import Field, SQLModel

class EstudanteCreate(SQLModel):
    nome: str
    numero_matricula: str 
    email: str
    curso_id: int

class EstudanteUpdate(SQLModel):
    nome: str | None = None
    numero_matricula: str | None = None
    email: str | None = None
    curso_id: int | None = None

class EstudanteRead(SQLModel):
    id: int
    nome: str
    numero_matricula: str
    email: str
    curso_id: int