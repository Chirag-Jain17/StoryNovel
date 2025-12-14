from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from core.config import settings

engine = create_engine(
    settings.DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal() #creates a session
    try:
        yield db #ensure multiple sessions are not open at the same time
    finally:
        db.close() #closes session when done

def create_tables():
    Base.metadata.create_all(bind=engine)