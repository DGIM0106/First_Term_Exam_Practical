from typing import Annotated
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from sqlmodel import SQLModel, Session
from sqlmodel import create_engine
import os

name_database = "FTE_db"

load_dotenv()

base_url = os.getenv("DATABASE_URL")

string_connection = base_url + name_database

engine = create_engine(string_connection, echo= True)

def create_all_tables(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]


