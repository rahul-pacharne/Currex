from app import app,login
from flask import render_template, flash, redirect,url_for
from flask_login import current_user, login_user, login_required
from flask_login import logout_user
from app.models import User, Wallet
from flask import request
from werkzeug.urls import url_parse
from app import db
from app.forms import RegistrationForm
from app.forms import LoginForm, ProfileForm, CreditForm, TransferForm
import os
from os.path import join, dirname, realpath
import requests

app.config['UPLOAD_PATH'] = join(dirname(realpath(__file__)), 'static/assets/images/user_images')

if 'API_KEY' in os.environ:
    API_KEY = os.environ['API_KEY']
else:
    API_KEY = 'RQM7GIDWT0ZU2WLU'

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
        from_c = current_user.default_currency
        current_user.default_currency = form.default_currency.data
        wallet = Wallet.query.filter_by(user_id=current_user.id).first()
        if(wallet):
            amount = wallet.amount
            amount = float(amount)
            
            to_c = form.default_currency.data
            url = 'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={}&to_currency={}&apikey={}'.format(from_c,to_c,API_KEY)
            
            # make the GET request to 'www.alphavantage.co' api service and then store the Response to 'response' variable
            response = requests.get(url=url).json()

            # calculating the amount according to the Currency Exchange Rate and store the value to 'result' variable 
            rate = response['Realtime Currency Exchange Rate']['5. Exchange Rate']
            rate = float(rate)
            result = rate * amount
            wallet.amount = result
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user'))
    return render_template('user.html', title='User Profile', form=form, user = current_user)

@app.route('/wallet', methods=['GET'])
def wallet():
    wallet = Wallet.query.filter_by(user_id=current_user.id).first()
    return render_template('wallet.html', title='Wallet', wallet=wallet)

@app.route('/credit', methods=['GET', 'POST'])
def credit():
    form = CreditForm()
    print("hello")
    if form.validate_on_submit():
        print("there")
        wallet = Wallet.query.filter_by(user_id=current_user.id).first()
        if(wallet):
            amount = form.amount.data
            amount = float(amount)
            from_c = request.form['currency']
            to_c = current_user.default_currency
            url = 'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={}&to_currency={}&apikey={}'.format(from_c,to_c,API_KEY)
            
            # make the GET request to 'www.alphavantage.co' api service and then store the Response to 'response' variable
            response = requests.get(url=url).json()

            # calculating the amount according to the Currency Exchange Rate and store the value to 'result' variable 
            rate = response['Realtime Currency Exchange Rate']['5. Exchange Rate']
            rate = float(rate)
            result = rate * amount
            wallet.amount = wallet.amount+result
            print(wallet.amount)
        
        else:
            wallet = Wallet(user_id = current_user.id,amount = form.amount.data )
            db.session.add(wallet)
        db.session.commit()
        flash('Congratulations, you added amount!')
        return redirect(url_for('wallet'))
    else:
        return render_template('credit.html', title='Credit amount', form=form)

@app.route('/debit', methods=['GET', 'POST'])
def debit():
    form = CreditForm()
    if form.validate_on_submit():
        wallet = Wallet.query.filter_by(user_id=current_user.id).first()
        if(wallet):
            amount = form.amount.data
            amount = float(amount)
            from_c = request.form['currency']
            to_c = current_user.default_currency
            url = 'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={}&to_currency={}&apikey={}'.format(from_c,to_c,API_KEY)
            
            # make the GET request to 'www.alphavantage.co' api service and then store the Response to 'response' variable
            response = requests.get(url=url).json()

            # calculating the amount according to the Currency Exchange Rate and store the value to 'result' variable 
            rate = response['Realtime Currency Exchange Rate']['5. Exchange Rate']
            rate = float(rate)
            result = rate * amount
            wallet.amount = wallet.amount-result
        
        
        db.session.commit()
        flash('Congratulations, you debited amount!')
        return redirect(url_for('wallet'))
    else:
        return render_template('credit.html', title='Credit amount', form=form)

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    form = TransferForm()
    print("hello")
    if form.validate_on_submit():
        print("there")
        wallet = Wallet.query.filter_by(user_id=current_user.id).first()
        to_user = User.query.filter_by(username=form.username.data).first()
        print(to_user)
        to_user_wallet = Wallet.query.filter_by(user_id=to_user.id).first()
        if(wallet):
            print("here I am in if1")
            amount = form.amount.data
            amount = float(amount)
            from_c = current_user.default_currency
            to_c = to_user.default_currency
            print("here I am in if")
            url = 'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={}&to_currency={}&apikey={}'.format(from_c,to_c,API_KEY)
            
            # make the GET request to 'www.alphavantage.co' api service and then store the Response to 'response' variable
            response = requests.get(url=url).json()

            # calculating the amount according to the Currency Exchange Rate and store the value to 'result' variable 
            rate = response['Realtime Currency Exchange Rate']['5. Exchange Rate']
            rate = float(rate)
            print("Conversion rate is:")
            print(rate)
            result = rate * amount
            wallet.amount = wallet.amount - amount
            db.session.flush()
            if(to_user_wallet):
                to_user_wallet.amount = to_user_wallet.amount + result
                print("here updated")
                print(to_user_wallet)
            else:
                to_user_wallet = Wallet(user_id = to_user.id,amount = result )
                db.session.add(to_user_wallet)
                print("here added")
            
        db.session.commit()
        flash('Congratulations, you added amount!')
        return redirect(url_for('wallet'))
    else:
        return render_template('transfer.html', title='Credit amount', form=form)
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))  
