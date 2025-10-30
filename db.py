from fastapi import FastAPI, Depends
from typing import Annotated
from sqlmodel import SQLModel, Session, create_engine

db_name = "MiTiendita.sqlite3"
db_url = f"sqlite:///{db_name}"
engine = create_engine(db_url)

def create_tables(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

def getSession():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(getSession)]