from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'T2xKNZBXZQEmwSpqJ5yv1SWrIwjXgeNQ'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/socialapp'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
# flash message style
login_manager.login_message_category = 'info'

from flaskproj import routes
from flaskproj.routes import users
app.register_blueprint(users)