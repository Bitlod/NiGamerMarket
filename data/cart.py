from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, orm
from data import db_session
from data.users import User
from data.products import Product


class Cart(SqlAlchemyBase, SerializerMixin):  # класс корзины
    __tablename__ = 'cart'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, nullable=False)
    name = Column(String)
    user_id = Column(Integer)
    price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
