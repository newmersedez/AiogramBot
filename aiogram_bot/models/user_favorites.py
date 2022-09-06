import sqlalchemy as sa
from sqlalchemy.orm import relationship
from aiogram_bot.models.base import Base


class UserFavorites(Base):
    __tablename__ = 'User_favorites'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('User.user_id', ondelete='CASCADE'), nullable=False)
    resource = sa.Column(sa.Text, nullable=False)
    user = relationship('User')
