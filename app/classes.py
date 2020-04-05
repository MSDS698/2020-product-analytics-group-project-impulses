from flask_login import UserMixin
from flask_wtf import FlaskForm

from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Optional
from datetime import datetime


from app import db, login_manager

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    phone = db.Column(db.String(10), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    signup_date = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow())
    status = db.Column(db.String(80), nullable=False, default='active')

    def __init__(self, first_name, last_name, email, phone, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.set_password(password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name:', validators=[DataRequired()])
    last_name = StringField('Last Name:', validators=[DataRequired()])
    email = StringField('Email Address:', validators=[DataRequired()])
    phone = StringField('Phone Number:', validators=[DataRequired()])
    password = PasswordField("Create a Password:", validators=[DataRequired()])
    submit = SubmitField("Submit")

class LogInForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    submit = SubmitField("Submit")

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


db.create_all()
db.session.commit()