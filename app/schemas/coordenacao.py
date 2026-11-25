from sqlmodel import SQLModel


class OfertaPeriodoRead(SQLModel):
    turma_id: int
    periodo: str
    codigo_disciplina: str
    nome_disciplina: str
    codigo_turma: str
    horario: str | None
    professor: str
    vagas: int
    vagas_ocupadas: int


class ResultadoTurmaRead(SQLModel):
    turma_id: int
    codigo_turma: str
    periodo: str
    codigo_disciplina: str
    nome_disciplina: str
    aprovados: int
    reprovados: int
    cancelados: int
    ativos: int
    total_matriculas: int