import ast
from sqlalchemy import MetaData, select


def parse_plaid_data(plaid_data):
    """
    Parse a string from plaid into python object
    :param plaid_data: name of the file (str)
    :return: list of dictionary
    """
    plaid_data = plaid_data.replace('\n', '')
    data = ast.literal_eval(plaid_data)
    return data


def add_accounts(db, accounts_data, user_id):
    """
    Add account information to the database
    :param db: database connection
    :param accounts_data: data with account information from Plaid (str)
    :param user_id: user id associated to the account (int)
    """
    accounts = parse_plaid_data(accounts_data)

    meta = MetaData(bind=db, reflect=True)
    with db.connect() as conn:
        select_statement = select([meta.tables['dw.plaid_items'].c.plaid_item_id]) \
            .where(meta.tables['dw.plaid_items'].c.user_id == user_id)
        result_set = conn.execute(select_statement)
        for r in result_set:
            plaid_id = r[0]
        for account in accounts:
            insert_statement = meta.tables['dw.accounts']. \
                insert().values(user_id=user_id, plaid_id=plaid_id,
                                account_plaid_id=account['account_id'],
                                account_name=account['name'],
                                account_type=account['type'],
                                account_subtype=account['subtype'])
            conn.execute(insert_statement)


def add_transactions(db, transactions_data):
    """
    Add account information to the database
    :param db: database connection
    :param transactions_data: data with transactions information
    from Plaid (str)
    """
    transactions = parse_plaid_data(transactions_data)

    meta = MetaData(bind=db, reflect=True)
    with db.connect() as conn:
        for transaction in transactions:
            select_statement = select(
                [meta.tables['dw.accounts'].c.user_id,
                 meta.tables['dw.accounts']
                     .c.account_id]).where(meta.tables['dw.accounts'].
                                           c.account_plaid_id ==
                                           transaction['account_id'])
            result_set = conn.execute(select_statement)
            for r in result_set:
                user_id = r[0]
                account_id = r[1]
            loc = transaction['location']
            categories = ';'.join(transaction['category'])
            insert_statement = meta.tables['dw.transaction']. \
                insert().values(user_id=user_id,
                                account_id=account_id,
                                trans_date=transaction['date'],
                                post_date=transaction['authorized_date'],
                                trans_amount=transaction['amount'],
                                merchant_category=categories,
                                merchant_address=loc['address'],
                                merchant_city=loc['city'],
                                merchant_state=loc['region'],
                                merchant_country=loc['country'],
                                merchant_postal_code=loc['postal_code'],
                                merchant_longitude=loc['lon'],
                                merchant_latitude=loc['lat'],
                                category_id=transaction['category_id'])
            conn.execute(insert_statement)
