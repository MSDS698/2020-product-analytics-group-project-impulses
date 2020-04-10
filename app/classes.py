"""
SQLAlchemy Object Relational Mapper (ORM) and Flask-WTForms

Including classes for each table in the database:
user, plaid_items, accounts, transaction, savings_history
and RegistrationForm and LogInForm
"""

from flask_login import UserMixin
from flask_wtf import FlaskForm

from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import PasswordField, StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length
from datetime import datetime

from app import db, login_manager


class User(db.Model, UserMixin):
    """Data model for user table.

    Columns include:
    user_id: auto increment primary key; bigint
    first_name: user's first name; string
    last_name: user's last name; string
    email: user's email address; string; unique
    phone: user's phone number; string; unique
    password_hash: user's hashed password; string
    signup_date: user's signup date; date
    status: user's current status; string
    auth_id: unique user id from OAuth if available; string
    """
    __tablename__ = 'user'
    id = db.Column('user_id', db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    phone = db.Column(db.String(10), unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    signup_date = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow())
    status = db.Column(db.String, nullable=False, default="active")
    auth_id = db.Column(db.String, default=None)
    # relationships
    plaid_items = db.relationship("PlaidItems", backref="user")
    accounts = db.relationship("Accounts", backref="user")
    transaction = db.relationship("Transaction", backref="user")
    savings_history = db.relationship("SavingsHistory", backref="user")
    habits = db.relationship("Habits", backref="user")

    def __init__(self, first_name, last_name, email,
                 phone, password, auth_id=None):
        """Initializes User class"""
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.auth_id = auth_id
        self.set_password(password)

    def set_password(self, password):
        """Generates a hashed password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the input password matches the actual password"""
        return check_password_hash(self.password_hash, password)


class PlaidItems(db.Model):
    """Data model for plaid_items table.

    Columns include:
    plaid_item_id: auto increment primary key; bigint
    user_id: user id that the plaid item is associated with; bigint
    item_id: plaid item id; string
    access_token: token that is associated to user account information
                  for retrieval in plaid; string
    """
    __tablename__ = 'plaid_items'
    id = db.Column('plaid_item_id', db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    item_id = db.Column(db.String, nullable=False)
    access_token = db.Column(db.String, nullable=False)
    # relationships
    accounts = db.relationship("Accounts", backref="plaid_item")


class Accounts(db.Model):
    """Data model for accounts table.

    Columns include:
    account_id: auto increment primary key; bigint
    user_id: user id that the account is associated with; bigint
    plaid_id: plaid id that the account is associated with; bigint
    account_plaid_id: unique id for identification in plaid; string
    account_name: account name; string
    account_type: account type, ex. investment/depository/credit; string
    account_subtype: account subtype, ex. 401k/checking/credit card; string
    """
    __tablename__ = "accounts"
    id = db.Column('account_id', db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    plaid_id = db.Column(db.Integer,
                         db.ForeignKey("plaid_items.plaid_item_id"))
    account_plaid_id = db.Column(db.String, nullable=False)
    account_name = db.Column(db.String)
    account_type = db.Column(db.String)
    account_subtype = db.Column(db.String)
    # relationships
    transaction = db.relationship("Transaction", backref="account")


class Transaction(db.Model):
    """Data model for transaction table.

    Columns include:
    transaction_id: auto increment primary key; bigint
    user_id: user id that the transaction is associated with; bigint
    account_id: account id that the transaction is associated with; bigint
    trans_amount: transaction amount; decimal(10, 2)
    category_id: category id in plaid; bigint
    is_preferred_saving: whether the transaction is a preferred saving
                         category; string
    trans_date: date of the transaction; date
    post_date: date when the transaction is posted on user's account; date
    merchant_category: multiple categories possible; string
    merchant_address: merchant address; string
    merchant_city: merchant city; string
    merchant_state: merchant state; string
    merchant_country: merchant country; string
    merchant_postal_code: merchant postal code; string
    merchant_longitude: merchant longitude; string
    merchant_latitude: merchant latitude; string
    """
    __tablename__ = "transaction"
    id = db.Column('transaction_id', db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    account_id = db.Column(db.Integer,
                           db.ForeignKey("accounts.account_id"))
    trans_amount = db.Column(db.Numeric(10, 2), nullable=False)
    category_id = db.Column(db.Integer)
    is_preferred_saving = db.Column(db.String)
    trans_date = db.Column(db.Date, nullable=False)
    post_date = db.Column(db.Date)
    merchant_category = db.Column(db.String)
    merchant_address = db.Column(db.String)
    merchant_city = db.Column(db.String)
    merchant_state = db.Column(db.String)
    merchant_country = db.Column(db.String)
    merchant_postal_code = db.Column(db.String)
    merchant_longitude = db.Column(db.String)
    merchant_latitude = db.Column(db.String)


class SavingsHistory(db.Model):
    """Data model for savings_history table.

    Columns include:
    savings_id: auto increment primary key; bigint
    user_id: id of the user that made the saving; bigint
    savings_amount: savings amount; decimal(10, 2)
    total_savings: total savings the user has made so far; decimal(10, 2)
    predicted_savings: predicted savings the user will make; decimal(10, 2)
    transfer_date: date when the savings are transferred to a
                   savings/investment account; date
    update_date: date when the savings entry is updated in the system; date
    """
    __tablename__ = "savings_history"
    id = db.Column('savings_id', db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    savings_amount = db.Column(db.Numeric(10, 2), nullable=False)
    total_savings = db.Column(db.Numeric(10, 2), nullable=False)
    predicted_savings = db.Column(db.Numeric(10, 2))
    transfer_date = db.Column(db.Date, nullable=False)
    update_date = db.Column(db.Date, nullable=False)


class Habits(db.Model):
    """Data model for habits table.

    Columns include:
    habits_id: auto increment primary key; bigint
    user_id: id of the user that made the habit; bigint
    habit_name: name of the habit user created; string
    habit_category: category of the habit; string
    time_minute: minute of the reminder; bigint (0-59)
    time_hour: hour of the reminder; bigint(0-23)
    """
    __tablename__ = "habits"
    id = db.Column("habits_id", db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    habit_name = db.Column(db.String, nullable=False)
    habit_category = db.Column(db.String, nullable=False)
    time_minute = db.Column(db.String, nullable=False)
    time_hour = db.Column(db.String, nullable=False)
    time_day_of_week = db.Column(db.String, nullable=False)

    def __init__(self, user_id, habit_name, habit_category, time_minute,
                 time_hour, time_day_of_week):
        self.user_id = user_id
        self.habit_name = habit_name
        self.habit_category = habit_category
        self.time_minute = time_minute
        self.time_hour = time_hour
        self.time_day_of_week = time_day_of_week


class RegistrationForm(FlaskForm):
    """Class for registration form"""
    first_name = StringField("First Name:",
                             validators=[
                                 DataRequired(message='Input Required')])
    last_name = StringField("Last Name:", validators=[
        DataRequired(message='Input Required')])
    email = StringField("Email Address:", validators=[
        DataRequired(message='Input Required')])
    phone = StringField("Phone Number:",
                        validators=[Length(min=10, max=10,
                                           message="Please put in 10 digits "
                                                   "valid phone number"
                                           )])
    password = PasswordField("Create a Password:", validators=[
        DataRequired(message='Input Required')])
    submit = SubmitField("Submit")


class LogInForm(FlaskForm):
    """Class for login form"""
    email = StringField("Email:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField("Submit")


class HabitForm(FlaskForm):
    """Class for habit formation form"""
    habit_name = StringField("Habit Name:", validators=[DataRequired()])
    habit_category = SelectField("Habit Category:",
                                 choices=[('Coffee', 'Coffee'),
                                          ('Lunch', 'Lunch'),
                                          ('Transportation',
                                           'Transportation')],
                                 validators=[DataRequired()])
    time_minute = SelectField("Minute:",
                              choices=[(str(i), str(i))
                                       for i in range(0, 60, 15)],
                              validators=[DataRequired()])
    time_hour = SelectField("Hour:", choices=[(str(i), str(i))
                                              for i in range(24)],
                            validators=[DataRequired()])
    time_day_of_week = SelectField("Day Of Week:",
                                   choices=[('1-5', 'Monday-Friday'),
                                            ('0,6', 'Weekends'),
                                            ('*', 'Everyday')],
                                   validators=[DataRequired()])
    submit = SubmitField("Submit")


@login_manager.user_loader
def load_user(id):
    """Return a user object from the user id stored in the session"""
    return User.query.get(int(id))


db.create_all()
db.session.commit()
