from app import db, classes
from datetime import datetime


def add_accounts(accounts, user, plaid_item, commit=True):
    """
    Add account information to the database
    :param accounts: accounts data from plaid api
    :param user: User SQLAlchemy object of the user associated with the
    accounts
    :param plaid_item: PlaidItem SQLalchemy object of the plaid_item associated
    with the accounts
    :param commit: If commit is True then commits transactions the add to the
    database
    """

    for account in accounts:
        acc = classes.Accounts(account_plaid_id=account['account_id'],
                               account_name=account['name'],
                               account_type=account['type'],
                               account_subtype=account['subtype'],
                               user=user,
                               plaid_item=plaid_item)
        db.session.add(acc)
    if commit is True:
        db.session.commit()


def add_transactions(transactions, user, account, commit=True):
    """
    Add account information to the database
    :param transactions: transactions data from plaid api
    :param user: User SQLAlchemy object of the user associated with the
    transactions
    :param account: Accounts SQLAlchemy object of the user associated with the
    transactions
    :param commit: If commit is True then commits transactions the add to the
    database
    """

    for transaction in transactions:
        loc = transaction['location']
        categories = ';'.join(transaction['category'])
        trans = classes.Transaction(user=user,
                                    account=account,
                                    trans_date=parse_date(transaction['date']),
                                    post_date=parse_date(
                                        transaction['authorized_date']),
                                    trans_amount=transaction['amount'],
                                    merchant_category=categories,
                                    merchant_address=loc['address'],
                                    merchant_city=loc['city'],
                                    merchant_state=loc['region'],
                                    merchant_country=loc['country'],
                                    merchant_postal_code=loc['postal_code'],
                                    merchant_longitude=loc['lon'],
                                    merchant_latitude=loc['lat'],
                                    category_id=transaction['category_id']
                                    )
        db.session.add(trans)
    if commit is True:
        db.session.commit()


def parse_date(date_string):
    try:
        return datetime.strptime(date_string, "%Y-%m-%d")
    except TypeError:
        return None
