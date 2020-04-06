"""
SQLAlchemy Object Relational Mapper (ORM) and Flask-WTForms

Including classes for each table in the database:
user, plaid_items, accounts, transaction, savings_history
and RegistrationForm and LogInForm
"""

from flask_login import UserMixin
from flask_wtf import FlaskForm

from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Optional
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
    __tablename__ = "user"
    id = db.Column("user_id", db.BigInteger, primary_key=True)
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
    plaid_id: auto increment primary key; bigint
    user_id: user id that the plaid item is associated with; bigint
    item_id: plaid item id; string
    access_token: token that is associated to user account information
                  for retrieval in plaid; string
    """
    __tablename__ = "plaid_items"
    id = db.Column("plaid_id", db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("user.user_id"))
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
    id = db.Column("account_id", db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("user.user_id"))
    plaid_id = db.Column(db.BigInteger,
                         db.ForeignKey("plaid_items.plaid_id"))
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
    id = db.Column("transaction_id", db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("user.user_id"))
    account_id = db.Column(db.BigInteger,
                           db.ForeignKey("accounts.account_id"))
    trans_amount = db.Column(db.Numeric(10, 2), nullable=False)
    category_id = db.Column(db.BigInteger)
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
    id = db.Column("savings_id", db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("user.user_id"))
    savings_amount = db.Column(db.Numeric(10, 2), nullable=False)
    total_savings = db.Column(db.Numeric(10, 2), nullable=False)
    predicted_savings = db.Column(db.Numeric(10, 2))
    transfer_date = db.Column(db.Date, nullable=False)
    update_date = db.Column(db.Date, nullable=False)


class RegistrationForm(FlaskForm):
    """Class for registration form"""
    first_name = StringField("First Name:", validators=[DataRequired()])
    last_name = StringField("Last Name:", validators=[DataRequired()])
    email = StringField("Email Address:", validators=[DataRequired()])
    phone = StringField("Phone Number:", validators=[DataRequired()])
    password = PasswordField("Create a Password:", validators=[DataRequired()])
    submit = SubmitField("Submit")


class LogInForm(FlaskForm):
    """Class for login form"""
    email = StringField("Email:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField("Submit")


@login_manager.user_loader
def load_user(id):
    """Return a user object from the user id stored in the session"""
    return User.query.get(int(id))


db.create_all()
db.session.commit()
