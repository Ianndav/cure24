from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from models import User, Listing
from forms import RegistrationForm, LoginForm, ListingForm, PaymentForm
from app import db

routes_bp = Blueprint('routes', __name__)

@routes_bp.route('/')
def home():
    return render_template('home.html', title='Welcome to Cure24')

@routes_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created. You can now log in.', 'success')
        return redirect(url_for('routes.login'))

    return render_template('register.html', title='Register', form=form)


