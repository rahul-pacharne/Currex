from app import app,login
from flask import render_template, flash, redirect,url_for
from flask_login import current_user, login_user, login_required
from flask_login import logout_user
from app.models import User
from flask import request
from werkzeug.urls import url_parse
from app import db
from app.forms import RegistrationForm
from app.forms import LoginForm, ProfileForm
import os
from os.path import join, dirname, realpath

app.config['UPLOAD_PATH'] = join(dirname(realpath(__file__)), 'static/assets/images/user_images')

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/user')
@login_required
def user():
    #user = User.query.filter_by(username=username).first_or_404()
    user = current_user
    form = ProfileForm()
    return render_template('user.html', user=user, form=form)
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], uploaded_file.filename))
            current_user.img_name = uploaded_file.filename
        current_user.default_currency = form.default_currency.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user'))
    return render_template('user.html', title='User Profile', form=form, user = current_user)
