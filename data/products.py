from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, orm
from data import db_session


class Product(SqlAlchemyBase, SerializerMixin):  # класс товаров
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)

    def delete(self, product_id):  # удаление товара 
        db_sess = db_session.create_session()
        product = db_sess.query(Product).get(product_id)
        if product:
            db_sess.delete(product)
            db_sess.commit()
            return True
        return False
