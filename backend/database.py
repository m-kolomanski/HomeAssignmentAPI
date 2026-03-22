from sqlmodel import Session, SQLModel, create_engine

from .config import settings

CONNECT_ARGS = {
    "check_same_thread": False
}

engine = create_engine(settings.DB_PATH, connect_args = CONNECT_ARGS)

def db_create():
    SQLModel.metadata.create_all(engine)

def db_get():
    with Session(engine) as session:
        yield session
