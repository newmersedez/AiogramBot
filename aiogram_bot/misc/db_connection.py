import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from aiogram_bot.models.base import Base
from aiogram_bot.config.bot_config import DATABASE_SQLALCHEMY_PATH


main_engine = sa.create_engine(
    DATABASE_SQLALCHEMY_PATH,
    echo=False,
)

DBSession = sessionmaker(
    binds={
        Base: main_engine,
    },
    expire_on_commit=False,
)


@contextmanager
def session_scope():
    session = DBSession()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
