"""
SQLAlchemy Object Relational Mapper (ORM)

Including classes for each table in the database:
user, plaid_items, accounts, transaction, savings_history
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from application import db


class User(db.Model, UserMixin):
    """Data model for dw.user table.

    Columns include:
    user_id: auto increment primary key; bigint
    auth_id: unique user id from OAuth; string
    first_name: user's first name; string
    last_name: user's last name; string
    email: user's email address; string; unique
    phone: user's phone number; string; unique
    password_hash: user's hashed password; string
    signup_date: user's signup date; date
    status: user's current status; string
    """
    __table_args__ = {"schema": "dw"}
    __tablename__ = "user"
    user_id = db.Column(db.BigInteger, primary_key=True)
    auth_id = db.Column(db.String)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    phone = db.Column(db.String(10), unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    signup_date = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow())
    status = db.Column(db.String, nullable=False, default="active")
    # relationships
    plaid_items = db.relationship("PlaidItems", backref="user")
    accounts = db.relationship("Accounts", backref="user")
    transaction = db.relationship("Transaction", backref="user")
    savings_history = db.relationship("SavingsHistory", backref="user")

    def __init__(self, auth_id, first_name, last_name,
                 email, phone, password):
        """Initializes User class"""
        self.auth_id = auth_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.set_password(password)

    def set_password(self, password):
        """Generates a hashed password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the input password matches the actual password"""
        return check_password_hash(self.password_hash, password)


class PlaidItems(db.Model):
    """Data model for dw.plaid_items table.

    Columns include:
    plaid_id: auto increment primary key; bigint
    user_id: user id that the plaid item is associated with; bigint
    item_id: plaid item id; string
    access_token: token that is associated to user account information
                  for retrieval in plaid; string
    """
    __table_args__ = {"schema": "dw"}
    __tablename__ = "plaid_items"
    plaid_id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("dw.user.user_id"))
    item_id = db.Column(db.String, nullable=False)
    access_token = db.Column(db.String, nullable=False)
    # relationships
    accounts = db.relationship("Accounts", backref="plaid_item")


class Accounts(db.Model):
    """Data model for dw.accounts table.

    Columns include:
    account_id: auto increment primary key; bigint
    user_id: user id that the account is associated with; bigint
    plaid_id: plaid id that the account is associated with; bigint
    account_plaid_id: unique id for identification in plaid; string
    account_name: account name; string
    account_type: account type, ex. investment/depository/credit; string
    account_subtype: account subtype, ex. 401k/checking/credit card; string
    """
    __table_args__ = {"schema": "dw"}
    __tablename__ = "accounts"
    account_id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("dw.user.user_id"))
    plaid_id = db.Column(db.BigInteger,
                         db.ForeignKey("dw.plaid_items.plaid_id"))
    account_plaid_id = db.Column(db.String, nullable=False)
    account_name = db.Column(db.String)
    account_type = db.Column(db.String)
    account_subtype = db.Column(db.String)
    # relationships
    transaction = db.relationship("Transaction", backref="account")


class Transaction(db.Model):
    """Data model for dw.transaction table.

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
    __table_args__ = {"schema": "dw"}
    __tablename__ = "transaction"
    transaction_id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("dw.user.user_id"))
    account_id = db.Column(db.BigInteger,
                           db.ForeignKey("dw.accounts.account_id"))
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
    """Data model for dw.savings_history table.

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
    __table_args__ = {"schema": "dw"}
    __tablename__ = "savings_history"
    savings_id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("dw.user.user_id"))
    savings_amount = db.Column(db.Numeric(10, 2), nullable=False)
    total_savings = db.Column(db.Numeric(10, 2), nullable=False)
    predicted_savings = db.Column(db.Numeric(10, 2))
    transfer_date = db.Column(db.Date, nullable=False)
    update_date = db.Column(db.Date, nullable=False)


db.create_all()
db.session.commit()
