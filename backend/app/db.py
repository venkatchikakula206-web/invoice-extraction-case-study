import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

_engine = None
_SessionLocal = None

class Base(DeclarativeBase):
    pass

def get_engine(settings):
    global _engine
    if _engine is None:
        _engine = create_engine(settings.database_url, future=True)
    return _engine

def get_session_factory(settings):
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine(settings)
        _SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)
    return _SessionLocal

def init_db(settings):
    os.makedirs(os.path.dirname(settings.upload_dir), exist_ok=True)
    os.makedirs(settings.upload_dir, exist_ok=True)
    # Ensure DB directory exists for sqlite relative paths
    if settings.database_url.startswith("sqlite:///./"):
        db_path = settings.database_url.replace("sqlite:///./", "./")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    from . import models  # noqa: F401
    engine = get_engine(settings)
    Base.metadata.create_all(bind=engine)
