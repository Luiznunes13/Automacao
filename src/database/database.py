"""
Configuração do banco de dados SQLAlchemy
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import logging

from src.config import settings
from .models import Base

logger = logging.getLogger(__name__)

# Engine do SQLAlchemy
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=False,  # True para debug SQL
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Inicializa o banco de dados criando todas as tabelas
    """
    logger.info("Inicializando banco de dados...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Banco de dados inicializado")


@contextmanager
def get_db() -> Session:
    """
    Context manager para obter sessão do banco de dados
    
    Usage:
        with get_db() as db:
            messages = db.query(Message).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Erro na transação do banco: {e}")
        raise
    finally:
        db.close()


def get_session() -> Session:
    """
    Retorna uma nova sessão (para uso sem context manager)
    Lembre-se de fechar com session.close()
    """
    return SessionLocal()
