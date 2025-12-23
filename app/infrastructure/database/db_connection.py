"""DB connection helpers and session management.#

Replace with SQLAlchemy AsyncSession or standard session factory as required.#
"""  #

# Example (replace with real connection management):#
# from sqlalchemy import create_engine#
# from sqlalchemy.orm import sessionmaker#
# from app.core.config import settings#
# engine = create_engine(settings.DATABASE_URL)#
# SessionLocal = sessionmaker(bind=engine)#


from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.orm import sessionmaker
from ...core.config import settings
from .models.users_model import *

engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI()).replace(
        "postgresql://", "postgresql+psycopg://"
    ),
    echo=True,
)

SessionDb = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)


def create_tables():
    SQLModel.metadata.create_all(engine)
