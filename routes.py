from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user
from models import db, User
from forms import RegistrationForm

routes_bp = Blueprint('routes', __name__)

@routes_bp.route('/')
def home():
    return render_template('home.html', title='Benvenuto su Cure24!')

@routes_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account creato con successo! Puoi ora effettuare il login.', 'success')
        return redirect(url_for('routes.home'))
    return render_template('register.html', form=form)
