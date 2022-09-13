import sqlalchemy as sa
from aiogram_bot.models import Base


class User(Base):
    __tablename__ = 'User'
    user_id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    username = sa.Column(sa.Text, nullable=False)
    last_index = sa.Column(sa.Integer)
    last_reply_command = sa.Column(sa.Text)
    last_keyboard = sa.Column(sa.Text)
    check_image_overview = sa.Column(sa.Integer)

    def __str__(self):
        return f'user_id = {self.user_id}, ' \
               f'username = {self.username}, ' \
               f'last_index = {self.last_index}, ' \
               f'last_reply_command = {self.last_reply_command}' \
               f'last_keyboard = {self.last_keyboard}'
