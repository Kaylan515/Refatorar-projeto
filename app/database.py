from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os

# Carrega variáveis do arquivo .env
load_dotenv()

# Se não encontrar DATABASE_URL no .env, usa SQLite como padrão
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///banco.db")

# Cria engine de conexão
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Configura sessão
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os models herdarem
class Base(DeclarativeBase):
    pass

# Dependência para injetar sessão no FastAPI
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
