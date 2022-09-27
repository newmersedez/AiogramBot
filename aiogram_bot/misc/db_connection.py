import os
import configparser
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from aiogram_bot.models import Base
from aiogram_bot.config import CONFIG_DIR


parser = configparser.ConfigParser()
parser.read(os.path.join(CONFIG_DIR, 'db_config.ini'))

HOST = parser.get('DATABASE_CONFIG', 'host')
DBNAME = parser.get('DATABASE_CONFIG', 'dbname')
USER = parser.get('DATABASE_CONFIG', 'user')
PASSWORD = parser.get('DATABASE_CONFIG', 'password')

main_engine = sa.create_engine(f'postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}/{DBNAME}')
DBSession = sessionmaker(
    binds={
        Base: main_engine,
    },
    expire_on_commit=False
)


# @contextmanager
# def session_scope():
#     session = DBSession()
#     try:
#         yield session
#         session.commit()
#     except Exception as e:
#         print('session_scope exc: ', e)
#         # session.rollback()
#         # raise e
#     finally:
#         session.close()
