# primary_key, foreign_key, autoincrement

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, orm
import datetime
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'
    id = Column(Integer, autoincrement=True, primary_key=True)
    surname = Column(String)
    name = Column(String)
    age = Column(Integer)
    position = Column(String)
    speciality = Column(String)
    address = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    modified_date = Column(DateTime, default=datetime.datetime.now)

    # jobs = orm.relationship('Jobs', back_populates='user')  # пользователь один, работ много; следовательно ...

    def __repr__(self):
        return f'<Colonist> {self.id} {self.surname} {self.name}'
