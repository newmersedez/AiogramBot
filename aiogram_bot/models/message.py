import sqlalchemy as sa
from aiogram_bot.models import Base


class Message(Base):
    __tablename__ = 'Message'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = sa.Column(sa.BigInteger, nullable=False)
    chat_id = sa.Column(sa.BigInteger, nullable=False)
    message_id = sa.Column(sa.BigInteger, nullable=False)

    def __str__(self):
        return f'id={self.id}, user_id = {self.user_id}, chat_id = {self.chat_id}, message_id = {self.message_id}'
