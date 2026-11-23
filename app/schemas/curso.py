from sqlmodel import SQLModel


class CursoCreate(SQLModel):
    nome : str

class CursoUpdate(SQLModel):
    nome : str

class CursoRead(SQLModel):
    id : int 
    nome : str