from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

application = Flask(__name__)
application.config.from_object(Config)

db = SQLAlchemy(application)
db.create_all()
db.session.commit()

login_manager = LoginManager()
login_manager.init_app(application)

bootstrap = Bootstrap(application)

from app import routes
from app import classes

if __name__ == '__main__':
    application.debug = True 
