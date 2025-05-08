import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager

# Logging
logging.basicConfig(level=logging.DEBUG)

# SQLAlchemy base
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Flask app
app = Flask(__name__)
app.secret_key = "questa-e-una-chiave-super-segreta-987654321"
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Inizializza il database
db.init_app(app)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Blueprint per le routes
from routes import routes_bp
app.register_blueprint(routes_bp)

# Crea tutte le tabelle se non esistono
with app.app_context():
    from models import User, Listing
    db.create_all()

# Avvio
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)  # Puoi cambiare porta se vuoi
