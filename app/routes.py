from app import app
from flask import render_template, flash, redirect,url_for
from flask_login import current_user, login_user, login_required
from flask_login import logout_user
from app.models import User
from flask import request
from werkzeug.urls import url_parse
from app import db
from app.forms import RegistrationForm

@app.route('/')
@app.route('/index')
def index():
    return "Hello John"


@app.route('/register', methods=['GET', 'POST'])
def register():
    #if current_user.is_authenticated:
        #return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(firstname = form.firstname.data, lastname = form.lastname.data ,default_currency = form.default_currency.data, username=form.username.data, email=form.email.data,)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)
