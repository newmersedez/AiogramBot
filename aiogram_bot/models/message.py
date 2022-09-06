import sqlalchemy as sa
from sqlalchemy.orm import relationship
from aiogram_bot.models.base import Base


class Message(Base):
    __tablename__ = 'Message'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('User.user_id', ondelete='CASCADE'), nullable=False)
    chat_id = sa.Column(sa.Integer, nullable=False)
    message_id = sa.Column(sa.Integer, nullable=False)
    user = relationship('User')

    def __str__(self):
        return f'id={self.id}, user_id = {self.user_id}, chat_id = {self.chat_id}, message_id = {message_id}'
