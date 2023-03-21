from flask import Flask, url_for, render_template, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec
from data import users
from data import jobs
from flask import Flask
from data.users import User
from data.jobs import Jobs
from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['FLASK_DEBUG'] = 1


@app.route('/')
def main_page():  # put application's code here
    return render_template('main_page.html')


@app.route('/products')
def products():  # put application's code here
    return render_template('products.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
