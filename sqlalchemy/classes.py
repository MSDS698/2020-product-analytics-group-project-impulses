"""
SQLAlchemy Object Relational Mapper (ORM)

Including classes for each table in the database:
user, password, plaid_items, accounts, transaction, savings_history
"""

from application import db


class User(db.Model):
    """Data model for dw.user table.

    Columns include:
    user_id: auto increment primary key; bigint
    auth_id: unique user id from OAuth; string
    first_name: user's first name; string
    last_name: user's last name; string
    email: user's email address; string
    phone: user's phone number; bigint
    signup_date: user's signup date; date
    status: user's current status; string
    """
    __table_args__ = {"schema": "dw"}
    __tablename__ = "user"
    user_id = db.Column("user_id", db.BigInteger, primary_key=True)
    auth_id = db.Column("auth_id", db.String, nullable=False)
    first_name = db.Column("first_name", db.String, nullable=False)
    last_name = db.Column("last_name", db.String, nullable=False)
    email = db.Column("email", db.String, nullable=False)
    phone = db.Column("phone", db.BigInteger, nullable=False)
    signup_date = db.Column("signup_date", db.Date, nullable=False)
    status = db.Column("status", db.String, nullable=False)

    def __init__(self, user_id, auth_id, first_name, last_name,
                 email, phone, signup_date, status):
        """Initializes User class"""
        self.user_id = user_id
        self.auth_id = auth_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.signup_date = signup_date
        self.status = status


class Password(db.Model):
    """Data model for dw.password table.

    Columns include:
    password_id: auto increment primary key; bigint
    user_id: user id that the password is associated with; bigint
    password: password hash; string
    """
    __table_args__ = {"schema": "dw"}
    __tablename__ = "password"
    password_id = db.Column("password_id", db.BigInteger, primary_key=True)
    user_id = db.Column("user_id", db.BigInteger, nullable=False)
    password = db.Column("password", db.String, nullable=False)

    def __init__(self, password_id, user_id, password):
        """Initializes Password class"""
        self.password_id = password_id
        self.user_id = user_id
        self.password = password


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
    plaid_id = db.Column("plaid_id", db.BigInteger, primary_key=True)
    user_id = db.Column("user_id", db.BigInteger, nullable=False)
    item_id = db.Column("item_id", db.String, nullable=False)
    access_token = db.Column("access_token", db.String, nullable=False)

    def __init__(self, plaid_id, user_id, item_id, access_token):
        """Initializes PlaidItems class"""
        self.plaid_id = plaid_id
        self.user_id = user_id
        self.item_id = item_id
        self.access_token = access_token


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
    account_id = db.Column("account_id", db.BigInteger, primary_key=True)
    user_id = db.Column("user_id", db.BigInteger, nullable=False)
    plaid_id = db.Column("plaid_id", db.BigInteger, nullable=False)
    account_plaid_id = db.Column("account_plaid_id", db.String,
                                 nullable=False)
    account_name = db.Column("account_name", db.String)
    account_type = db.Column("account_type", db.String)
    account_subtype = db.Column("account_subtype", db.String)

    def __init__(self, account_id, user_id, plaid_id, account_plaid_id,
                 account_name, account_type, account_subtype):
        """Initializes Accounts class"""
        self.account_id = account_id
        self.user_id = user_id
        self.plaid_id = plaid_id
        self.account_plaid_id = account_plaid_id
        self.account_name = account_name
        self.account_type = account_type
        self.account_subtype = account_subtype


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
    transaction_id = db.Column("transaction_id", db.BigInteger,
                               primary_key=True)
    user_id = db.Column("user_id", db.BigInteger, nullable=False)
    account_id = db.Column("account_id", db.BigInteger, nullable=False)
    trans_amount = db.Column("trans_amount", db.Numeric(10, 2),
                             nullable=False)
    category_id = db.Column("category_id", db.BigInteger, nullable=False)
    is_preferred_saving = db.Column("is_preferred_saving", db.String)
    trans_date = db.Column("trans_date", db.Date, nullable=False)
    post_date = db.Column("post_date", db.Date)
    merchant_category = db.Column("merchant_category", db.String)
    merchant_address = db.Column("merchant_address", db.String)
    merchant_city = db.Column("merchant_city", db.String)
    merchant_state = db.Column("merchant_state", db.String)
    merchant_country = db.Column("merchant_country", db.String)
    merchant_postal_code = db.Column("merchant_postal_code", db.String)
    merchant_longitude = db.Column("merchant_longitude", db.String)
    merchant_latitude = db.Column("merchant_latitude", db.String)

    def __init__(self, transaction_id, user_id, account_id, trans_amount,
                 category_id, is_preferred_saving, trans_date, post_date,
                 merchant_category, merchant_address, merchant_city,
                 merchant_state, merchant_country, merchant_postal_code,
                 merchant_longitude, merchant_latitude):
        """Initializes Transaction class"""
        self.transaction_id = transaction_id
        self.user_id = user_id
        self.account_id = account_id
        self.trans_amount = trans_amount
        self.category_id = category_id
        self.is_preferred_saving = is_preferred_saving
        self.trans_date = trans_date
        self.post_date = post_date
        self.merchant_category = merchant_category
        self.merchant_address = merchant_address
        self.merchant_city = merchant_city
        self.merchant_state = merchant_state
        self.merchant_country = merchant_country
        self.merchant_postal_code = merchant_postal_code
        self.merchant_longitude = merchant_longitude
        self.merchant_latitude = merchant_latitude


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
    savings_id = db.Column("savings_id", db.BigInteger, primary_key=True)
    user_id = db.Column("user_id", db.BigInteger, nullable=False)
    savings_amount = db.Column("savings_amount", db.Numeric(10, 2),
                               nullable=False)
    total_savings = db.Column("total_savings", db.Numeric(10, 2),
                              nullable=False)
    predicted_savings = db.Column("predicted_savings", db.Numeric(10, 2))
    transfer_date = db.Column("transfer_date", db.Date, nullable=False)
    update_date = db.Column("update_date", db.Date, nullable=False)

    def __init__(self, savings_id, user_id, savings_amount, total_savings,
                 predicted_savings, transfer_date, update_date):
        """Initializes SavingsHistory class"""
        self.savings_id = savings_id
        self.user_id = user_id
        self.savings_amount = savings_amount
        self.total_savings = total_savings
        self.predicted_savings = predicted_savings
        self.transfer_date = transfer_date
        self.update_date = update_date


db.create_all()
db.session.commit()
