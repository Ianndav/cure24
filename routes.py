from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from models import User

routes_bp = Blueprint('routes', __name__)

@routes_bp.route('/')
def home():
    return render_template('home.html', title='Welcome to Cure24')

@routes_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Esempio semplice. Dovresti avere una LoginForm qui.
    return "Pagina di login (da implementare)"
