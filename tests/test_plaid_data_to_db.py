import unittest
import os
from datetime import datetime
from plaid_methods import add_plaid_data, methods
from app import application, db, classes
from plaid import Client
from plaid.api import sandbox


ENV_VARS = {
    "PLAID_CLIENT_ID": os.environ["PLAID_CLIENT_ID"],
    "PLAID_PUBLIC_KEY": os.environ["PLAID_PUBLIC_KEY"],
    "PLAID_SECRET": os.environ["PLAID_SECRET"],
}
INSTITUTION_ID = 'ins_109508'
INITIAL_PRODUCTS = ['transactions']


class TestDataToDB(unittest.TestCase):
    """Class for testing the database"""

    def setUp(self):
        """Initialization for the test cases

        This is executed prior to each test.
        """
        application.config['TESTING'] = True
        application.config['WTF_CSRF_ENABLED'] = False
        application.config['DEBUG'] = False
        self.app = application.test_client()
        # setup plaid client
        self.client = Client(
            ENV_VARS["PLAID_CLIENT_ID"],
            ENV_VARS["PLAID_SECRET"],
            ENV_VARS["PLAID_PUBLIC_KEY"],
            "sandbox"
        )
        self.public_token = sandbox.PublicToken(self.client)
        db.drop_all()
        db.create_all()

        # Create a test user and test plaid item
        self.test_user = classes.User(first_name="first", last_name="last",
                                      email="test@gmail.com", phone="9876543210",
                                      password="password")
        db.session.add(self.test_user)
        db.session.commit()
        self.test_item = classes.PlaidItems(user=self.test_user, item_id="item",
                                            access_token="token")
        db.session.add(self.test_item)
        db.session.commit()

    def tearDown(self):
        """Clean-up for the test cases

        This is executed after each test.
        """
        db.session.remove()

    ####################################################################
    # Add data to Database Tests
    ####################################################################

    def test_add_account(self):
        """Test if accounts data are correctly inserted in the database
        """
        # Get accounts to be added
        response = self.public_token.create(INSTITUTION_ID,
                                            INITIAL_PRODUCTS)

        response = methods.token_exchange(self.client,
                                          response['public_token'])
        access_token = response['access_token']
        accounts = methods.get_accounts(self.client, access_token)
        add_plaid_data.add_accounts(accounts, self.test_user, self.test_item, commit=True)
        account = classes.Accounts.query.first()
        self.assertEqual(account.user_id, self.test_user.id, msg="check user id")
        self.assertEqual(account.plaid_id, self.test_item.id, msg="check plaid item id")
        self.assertEqual(account.account_plaid_id, accounts[0]['account_id'],
                         msg="check account plaid id")
        self.assertEqual(account.account_name, accounts[0]['name'],
                         msg="check account name")
        self.assertEqual(account.account_type, accounts[0]['type'],
                         msg="check account type")
        self.assertEqual(account.account_subtype, accounts[0]['subtype'],
                         msg="check account subtype")

    def test_add_transactions(self):
        """Test if transactions data are correctly inserted in the database
        """
        response = self.public_token.create(INSTITUTION_ID,
                                            INITIAL_PRODUCTS)
        response = methods.token_exchange(self.client,
                                          response['public_token'])
        access_token = response['access_token']
        accounts = methods.get_accounts(self.client, access_token)
        add_plaid_data.add_accounts(accounts, self.test_user, self.test_item, commit=True)
        start_date = "2019-01-01"
        end_date = "2020-04-01"
        transactions = methods.get_transactions(self.client,
                                                start_date,
                                                end_date,
                                                access_token,
                                                accounts[0]['account_id'])
        account = classes.Accounts.query.first()
        add_plaid_data.add_transactions(transactions, self.test_user, account, commit=True)
        transaction = classes.Transaction.query.filter_by(account_id=account.id).first()
        categories = ';'.join(transactions[0]['category'])
        self.assertEqual(transaction.user_id, self.test_user.id, msg="check user id")
        self.assertEqual(transaction.account_id, account.id, msg="check account id")
        self.assertEqual(str(transaction.trans_amount), str(transactions[0]['amount']),
                         msg="check transaction amount")
        self.assertEqual(datetime.strftime(transaction.trans_date, "%Y-%m-%d"), transactions[0]['date'],
                         msg="check transaction date")
        self.assertEqual(transaction.merchant_category, categories,
                         msg="check merchant category")
        self.assertEqual(transaction.merchant_address, transactions[0]['location']['address'],
                         msg="check merchant address")
        self.assertEqual(transaction.merchant_city, transactions[0]['location']['city'],
                         msg="check merchant city")
        self.assertEqual(transaction.merchant_state, transactions[0]['location']['region'],
                         msg="check merchant state")
        self.assertEqual(transaction.merchant_country, transactions[0]['location']['country'],
                         msg="check merchant country")
        self.assertEqual(transaction.merchant_postal_code, transactions[0]['location']['postal_code'],
                         msg="check merchant postal code")
        self.assertEqual(transaction.merchant_longitude, transactions[0]['location']['lon'],
                         msg="check merchant longitude")
        self.assertEqual(transaction.merchant_latitude, transactions[0]['location']['lat'],
                         msg="check merchant latitude")
        self.assertEqual(str(transaction.category_id), transactions[0]['category_id'],
                         msg="check category id")


if __name__ == "__main__":
    unittest.main()
