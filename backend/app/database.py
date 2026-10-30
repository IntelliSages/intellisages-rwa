from collections.abc import Generator
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./rwa-intelligence.db")
APP_ENV = os.getenv("APP_ENV", "development")
if APP_ENV == "production" and not DATABASE_URL.startswith(("postgresql://", "postgresql+")):
    raise RuntimeError("Production requires a PostgreSQL DATABASE_URL.")
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, class_=Session)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
