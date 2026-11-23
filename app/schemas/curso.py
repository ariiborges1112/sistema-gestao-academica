from sqlmodel import SQLModel


class CursoCreate(SQLModel):
    nome : str

class CursoUpdate(SQLModel):
    nome : str | None = None

class CursoRead(SQLModel):
    id : int 
    nome : str