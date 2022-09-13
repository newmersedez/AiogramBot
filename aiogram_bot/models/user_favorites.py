import sqlalchemy as sa
from aiogram_bot.models import Base


class UserFavorites(Base):
    __tablename__ = 'User_favorites'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = sa.Column(sa.Integer, nullable=False)
    resource = sa.Column(sa.Text, nullable=False)
    resource_type = sa.Column(sa.Text, nullable=False)
