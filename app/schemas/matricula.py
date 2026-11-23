from datetime import date
from sqlmodel import SQLModel, Field
from app.models.matricula import StatusMatricula

class MatriculaCreate(SQLModel):
    estudante_id: int 
    turma_id: int 

class MatriculaDesempenhoUpdate(SQLModel):
    nota: float | None = Field(default=None, ge=0, le=10)
    frequencia: float | None = Field(default=None, ge=0, le=100)

class MatriculaRead(SQLModel):
    id: int 
    estudante_id: int
    turma_id: int
    status: StatusMatricula
    nota: float | None 
    frequencia: float | None
    data_matricula: date
    data_cancelamento: date | None