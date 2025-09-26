import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Usar SQLite para desarrollo
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./neototem.db")

# Para SQLite, agregar configuraciones específicas
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # Cambiar a True para debug
        connect_args={"check_same_thread": False}  # Necesario para SQLite con FastAPI
    )
else:
    engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency para usar en FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
