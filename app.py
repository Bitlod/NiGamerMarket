from flask import render_template, redirect, request, flash, url_for
from flask import Flask

import data
from data import db_session, products, users
from forms.registration import RegistrationForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.login import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['FLASK_DEBUG'] = 1
login_manager = LoginManager()
login_manager.init_app(app)


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
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        flash('Регистрация прошла успешно', 'success')  # Выдача сообщения об успешной регистрации
        return redirect('/login')
    return render_template('registration.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    User = data.users.User
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    User = data.users.User
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        flash('Неправильный логин или пароль', 'danger')
        return redirect('/login')
    return render_template('login.html', title='Авторизация', form=form)


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
                if product_to_delete.user_id == current_user.id:
                    # Удаляем объект из сессии и базы данных
                    product_to_delete.delete(product_id)
                    flash('Товар удален', 'success')
                    return redirect('/products')
                else:
                    flash('Вы не можете удалить данный товар', 'danger')
            else:
                flash('Ошибка при удалении товара', 'error')
        else:
            # Получаем данные из формы
            name = request.form['name']
            price = int(request.form['price'])
            # Создаем новый объект Product
            new_product = Product()
            new_product.name = name
            new_product.price = price
            print(current_user)
            new_product.user_id = current_user.id
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


@app.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    Product = data.products.Product
    db_sess = db_session.create_session()
    product = db_sess.query(Product).get(product_id)
    if product:
        # Проверяем, соответствует ли текущий пользователь пользователю-владельцу товара
        if product.user_id == current_user.id:
            db_sess.delete(product)
            db_sess.commit()
            flash('Товар успешно удален', 'success')
        else:
            flash('Вы не можете удалить данный товар', 'danger')
    else:
        flash('Товар не найден', 'danger')
    return redirect(url_for('products'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


def main():
    db_session.global_init('products.db')
    app.run(debug=True)


if __name__ == '__main__':
    main()
