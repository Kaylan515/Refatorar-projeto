from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine =  create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} #evitar problemas, importante
)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine) #mesma coisa no nosso projeto

class Base(DeclarativeBase):
    pass #todo mundo q herdar da Base, vai conseguir fazer conexão com o banco

def get_db():
    db = Session()
    try:
        yield db #yield garante q a sessão vai ser enviada e fechada automaticamente 
    finally:
        db.close()