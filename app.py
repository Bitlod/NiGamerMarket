from flask import render_template, redirect, request, flash, url_for, session
from flask import Flask
from flask_ngrok import run_with_ngrok

import data
from data import db_session, products, users, cart
from forms.registration import RegistrationForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.login import LoginForm
from sqlalchemy.orm import Query
from flask_wtf.csrf import CSRFProtect
from flask_uploads import UploadSet, IMAGES
from werkzeug.utils import secure_filename
from flask_dropzone import Dropzone
import os

# Создаем экземпляр CSRFProtect
csrf = CSRFProtect()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['FLASK_DEBUG'] = 1
# дебаг нужен для отлавливания и исправления ошибок в реальном времени 
login_manager = LoginManager()
login_manager.init_app(app)
csrf.init_app(app)  # csrf токен для предотвращения поддельных запросов

# создаем экземпляры расширений
photos = UploadSet('photos', IMAGES)
dropzone = Dropzone(app)

# добавляем конфигурацию для загрузки файлов
app.config['UPLOAD_FOLDER'] = 'static/uploads/photos'
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image'
app.config['DROPZONE_MAX_FILES'] = 1
app.config['DROPZONE_UPLOAD_MULTIPLE'] = False


def format_goods_count(count: int):
    if count % 10 == 1 and count % 100 != 11:
        return f"{count} предмет"
    elif count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
        return f"{count} предмета"
    else:
        return f"{count} предметов"


@app.route('/registration', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    User = data.users.User
    db_sess = db_session.create_session()
    if form.validate_on_submit():  # если форма регистрации на подтверждение, то...
        if form.password.data != form.confirm_password.data:
            flash(message='Пароли не совпадают',
                  category='danger')  # Выдача предупреждения на следующую страницу, в html файле есть обработчик
            # для flash предупреждений (далее также)
            return redirect('/registration')  # Перенаправление на страницу регистрации
        if db_sess.query(User).filter(User.username == form.username.data).first():
            flash(message='Пользователь с таким именем пользователя уже существует', category='warning ')
            return redirect('/registration')  # Перенаправление на страницу регистрации
        user = User()
        user.username = form.username.data
        user.password = form.password.data
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        flash(message='Регистрация прошла успешно', category='success')  # Выдача сообщения об успешной регистрации
        return redirect('/login')
    return render_template('registration.html', title='Регистрация', form=form)


@login_manager.user_loader  # для сессии
def load_user(user_id):
    User = data.users.User
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')  # выход
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
        if user and user.check_password(form.password.data):  # проверяет хеш пароля через функцию внутри класса юзер
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        flash(message='Неправильный логин или пароль', category='danger')
        return redirect('/login')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/')  # главная страница 
def main_page():
    Product = data.products.Product
    db_sess = db_session.create_session()
    products = db_sess.query(Product).limit(3).all()  # выбор 3 продуктов для отображения на главной странице 
    d = {'src1': url_for('static', filename='img/mars2.jpg'),
         'src2': url_for('static', filename='img/mars1.jpg'),
         'src3': url_for('static', filename='img/mars3.jpg')}
    # Проверка на наличие товаров
    if products:
        return render_template('main_page.html', products=products, enumerate=enumerate, **d)
    else:
        return render_template('main_page.html', products=[], enumerate=enumerate, **d)


# добавляем обработчик для загрузки файлов
@app.route('/upload', methods=['POST'])
def upload_photo():
    file = request.files.get('file')
    if file:
        filename = photos.save(file)
        return filename
    else:
        return 'error'


@app.route('/products', methods=['GET', 'POST'])  # страница товаров
def products():
    db_sess = db_session.create_session()
    Product = data.products.Product

    if request.method == 'POST':
        if 'delete' in request.form:  # если нажата кнопка удалить 
            # Получаем ID продукта для удаления
            product_id = int(request.form['delete'])
            # Находим объект Product по ID
            product_to_delete = db_sess.query(Product).get(product_id)
            if product_to_delete:  # если такой есть:
                if product_to_delete.user_id == current_user.id:  # если пользователь хочет удалить свой товар
                    # Удаляем объект из сессии и базы данных
                    product_to_delete.delete(product_id)
                    flash(message='Товар удален', category='success')
                    return redirect('/products')
                else:
                    flash(message='Вы не можете удалить данный товар', category='warning')
            else:
                flash(message='Ошибка при удалении товара', category='danger')
        else:  # добавление товара
            # Получаем данные из формы
            name = request.form['name']
            price = int(request.form['price'])
            description = request.form['description']
            # Создаем новый объект Product
            new_product = Product()
            new_product.name = name  # добавляем в бд название товара
            new_product.price = price  # цену
            new_product.description = description  # описание

            image = request.files['image']
            if image:
                # сохранение файла изображения в папке "uploads"
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_product.image = filename

            new_product.user_id = current_user.id  # добавление в бд ид текущего пользователя 
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


@app.route('/products/sort', methods=['POST'])  # сортировка на странице товаров
def sort_products():
    products = None  # нужно для передачи на страницу с продуктами (ну или же можно удалить)
    sort_by = request.form['sort_by']
    db_sess = db_session.create_session()
    Product = data.products.Product
    if sort_by == 'name':  # сортировка по имени
        products = db_sess.query(Product).order_by(Product.name)
    elif sort_by == 'price':  # по цене
        products = db_sess.query(Product).order_by(Product.price)
    return render_template('products.html', products=products)


@app.route('/delete_product/<int:product_id>', methods=['POST'])
# удаление товаров доступно для зарегистрированных пользователей, и удаление только того, что добавили они сами,
# поэтому конкретная функция для удаления
@login_required  # нельзя удалить если не зареган 
def delete_product(product_id):
    Product = data.products.Product
    db_sess = db_session.create_session()
    product = db_sess.query(Product).get(product_id)
    if product:
        # Проверяем, соответствует ли текущий пользователь пользователю-владельцу товара
        if product.user_id == current_user.id:
            db_sess.delete(product)
            db_sess.commit()
            flash(message='Товар успешно удален', category='success')
        else:
            flash(message='Вы не можете удалить данный товар', category='warning')
    else:
        flash(message='Товар не найден', category='danger')
    return redirect(url_for('products'))


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


@app.route('/cart', methods=['POST', 'GET'])
def cart():
    db_sess = db_session.create_session()
    Cart = data.cart.Cart
    if request.method == 'POST':
        product_id = request.form['product_id']
        add_to_cart(product_id)
        flash(message='Товар добавлен в корзину', category='success')
        return redirect(url_for('cart'))
    else:
        cart_items = db_sess.query(Cart).filter_by(user_id=current_user.id).all()
        total = sum(item.price * item.quantity for item in cart_items)
        return render_template('cart.html', items=cart_items, total=total, format_goods_count=format_goods_count)


@app.route("/add_to_cart/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id, quantity=1):
    # Получаем информацию о товаре из базы данных
    db_sess = db_session.create_session()
    Product = data.products.Product
    Cart = data.cart.Cart
    # Получаем информацию о товаре
    cart_item = db_sess.query(Cart).filter_by(product_id=product_id, user_id=current_user.id).first()
    if cart_item:
        cart_item.quantity += quantity
        db_sess.commit()
    else:
        product = db_sess.query(Product).filter_by(id=product_id).first()
        # Проверяем, что такой товар существует
        if product is not None:
            # Добавляем товар в корзину
            cart_item = Cart(product_id=product.id,
                             name=product.name,
                             user_id=current_user.id,
                             price=product.price,
                             quantity=1)
            db_sess.add(cart_item)
            db_sess.commit()
    flash(message='Товар успешно добавлен в корзину!', category='product')
    return redirect(url_for('product_detail', product_id=product_id))


@app.route('/delete_item/<int:item_id>')
def delete_item(item_id):
    db_sess = db_session.create_session()
    Product = data.products.Product
    Cart = data.cart.Cart
    item = db_sess.query(Cart).get(item_id)
    if item.quantity > 1:
        item.quantity -= 1
        db_sess.commit()
    else:
        db_sess.delete(item)
        db_sess.commit()
    return redirect('/cart')


@app.route('/delete_all_items/<int:product_id>')
def delete_all_items(product_id):
    db_sess = db_session.create_session()
    Product = data.products.Product
    Cart = data.cart.Cart
    items = db_sess.query(Cart).filter_by(product_id=product_id, user_id=current_user.id).all()
    for item in items:
        db_sess.delete(item)
        db_sess.commit()
    return redirect('/cart')


@app.route('/delete_all_user_items')
def delete_all_user_items():
    db_sess = db_session.create_session()
    Product = data.products.Product
    Cart = data.cart.Cart
    items = db_sess.query(Cart).filter_by(user_id=current_user.id).all()
    for item in items:
        db_sess.delete(item)
        db_sess.commit()
    return redirect('/cart')


@app.route("/buy")
@login_required
def buy():
    return render_template('buy.html')


@app.route("/products/<int:product_id>", methods=['POST', 'GET'])
def product_detail(product_id):
    # Получаем информацию о товаре из базы данных
    db_sess = db_session.create_session()
    Product = data.products.Product
    product = db_sess.query(Product).get(product_id)

    # Отображаем шаблон с информацией о товаре
    return render_template("product_detail.html", product=product)


@app.route("/checkout", methods=['POST', 'GET'])
def checkout():
    return render_template('checkout.html')


@app.errorhandler(404)  # обработчик 404
def not_found_error(error):
    return render_template('404.html'), 404


def main():
    db_session.global_init('products.db')
    app.run(debug=True)


if __name__ == '__main__':
    main()
