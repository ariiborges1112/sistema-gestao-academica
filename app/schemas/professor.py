from sqlmodel import SQLModel

class ProfessorCreate(SQLModel):
    nome: str
    email: str

class ProfesorUpdate(SQLModel):
    nome: str | None = None
    email: str | None = None

class ProfessorRead(SQLModel):
    id: int
    nome: str
    email: str 

    