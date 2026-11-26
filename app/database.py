from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

DATABASE_URL = settings.DATABASE_URL
is_sqlite = DATABASE_URL.startswith("sqlite")

connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    connect_args=connect_args,
)

if is_sqlite:
    @event.listens_for(engine, "connect")
    def ativar_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_db_and_tables():
    # Mantida apenas para scripts de teste; o schema oficial é gerenciado pelo Alembic.
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session