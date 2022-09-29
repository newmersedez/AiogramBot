import sqlalchemy as sa
from aiogram_bot.models import Base


class UserFavorites(Base):
    __tablename__ = 'User_favorites'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = sa.Column(sa.Integer, nullable=False)
    resource = sa.Column(sa.Text, nullable=False)
    resource_type = sa.Column(sa.Text, nullable=False)

    def __str__(self):
        return f'user_id = {self.user_id}, ' \
               f'resource = {self.resource}, ' \
               f'resource_type = {self.resource_type}'
