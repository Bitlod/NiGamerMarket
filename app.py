from flask import Flask, url_for, render_template, redirect, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec
import data
from flask import Flask
from data import db_session
from data.registration import RegistrationForm
from random import randint

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['FLASK_DEBUG'] = 1


@app.route('/registration', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    User = data.users.User
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        if form.password.data != form.confirm_password.data:
            flash('Пароли не совпадают', 'danger')  # Выдача предупреждения
            return redirect('/registration')  # Перенаправление на страницу регистрации
        if db_sess.query(User).filter(User.username == form.username.data).first():
            flash('Пользователь с таким именем пользователя уже существует', 'danger')  # Выдача предупреждения
            return redirect('/registration')  # Перенаправление на страницу регистрации
        user = User()
        user.username = form.username.data
        user.password = form.password.data
        db_sess.add(user)
        db_sess.commit()
        flash('Регистрация прошла успешно', 'success')  # Выдача сообщения об успешной регистрации
        return redirect('/registration')
    return render_template('registration.html', title='Регистрация', form=form)
# тут почти рабочая из урока, в тхт файле другую сам написал, но ошибка. потом разберусь


@app.route('/')
def main_page():
    Product = data.products.Product
    db_sess = db_session.create_session()
    products = db_sess.query(Product).limit(3).all()

    # Проверка на наличие товаров
    if products:
        return render_template('main_page.html', products=products)
    else:
        return render_template('main_page.html', products=[])


@app.route('/products', methods=['GET', 'POST'])
def index():
    db_sess = db_session.create_session()
    Product = data.products.Product

    if request.method == 'POST':
        if 'delete' in request.form:
            # Получаем ID продукта для удаления
            product_id = int(request.form['delete'])
            # Находим объект Product по ID
            product_to_delete = db_sess.query(Product).get(product_id)
            if product_to_delete:
                # Удаляем объект из сессии и базы данных
                db_sess.delete(product_to_delete)
                db_sess.commit()
        else:
            # Получаем данные из формы
            name = request.form['name']
            price = int(request.form['price'])
            # Создаем новый объект Product
            new_product = Product()
            new_product.name = name
            new_product.price = price
            # Добавляем объект в сессию
            db_sess.add(new_product)
            # Сохраняем изменения в базе данных
            db_sess.commit()
        # Перенаправляем на главную страницу
        return redirect('/products')
    else:
        # Получаем все продукты из базы данных
        products = db_sess.query(Product).all()
        # Отправляем данные на шаблон и рендерим страницу
        return render_template('products.html', products=products)


@app.route('/products/sort', methods=['POST'])
def sort_products():
    global products
    sort_by = request.form['sort_by']
    db_sess = db_session.create_session()
    Product = data.products.Product
    if sort_by == 'name':
        products = db_sess.query(Product).order_by(Product.name)
    elif sort_by == 'price':
        products = db_sess.query(Product).order_by(Product.price)
    return render_template('products.html', products=products)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


def main():
    db_session.global_init('products.db')
    app.run(debug=True)


if __name__ == '__main__':
    main()
