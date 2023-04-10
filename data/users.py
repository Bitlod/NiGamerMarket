# primary_key, foreign_key, autoincrement

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, orm
import datetime
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'users'
    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
