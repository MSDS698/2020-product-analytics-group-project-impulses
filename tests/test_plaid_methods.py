import os
import unittest
import flask
from plaid_methods import methods
from plaid import Client
from plaid.api import sandbox

TEST_DB = 'test.db'
BASEDIR = os.path.abspath(os.path.dirname(__file__))
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(BASEDIR, TEST_DB)

from app import application, classes, db
from plaid.errors import PlaidError
ENV_VARS = {
    "PLAID_CLIENT_ID": os.environ["PLAID_CLIENT_ID"],
    "PLAID_PUBLIC_KEY": os.environ["PLAID_PUBLIC_KEY"],
    "PLAID_SECRET": os.environ["PLAID_SECRET"],
    "PLAID_ENV": os.environ["PLAID_ENV"]
}

INSTITUTION_ID = 'ins_109508'
INITIAL_PRODUCTS = ['transactions']
TEST_OPTION_TRANSACTION =  \
        {
            "override_username": "user_custom",
            "override_password": \
            """{
                "override_accounts": [
                    {
                        "type": "depository",
                        "subtype": "checking",
                        "transactions": [
                            {
                                "date_transacted": "2019-10-10",
                                "date_posted": "2019-10-03",
                                "currency": "USD",
                                "amount": 100,
                                "description": "1 year Netflix subscription"
                            },
                            {
                                "date_transacted": "2019-10-01",
                                "date_posted": "2019-10-02",
                                "currency": "USD",
                                "amount": 100,
                                "description": "1 year mobile subscription"
                            }
                        ]
                    }
                ]
            }
            """
        }


class TestSetup(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        application.config['TESTING'] = True
        application.config['WTF_CSRF_ENABLED'] = False
        application.config['DEBUG'] = False
        application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(BASEDIR, TEST_DB)
        self.app = application.test_client()
        # setup plaid client
        self.client = Client(
            ENV_VARS["PLAID_CLIENT_ID"],
            ENV_VARS["PLAID_SECRET"],
            ENV_VARS["PLAID_PUBLIC_KEY"],
            ENV_VARS["PLAID_ENV"],
        )
        self.public_token = sandbox.PublicToken(self.client)
        db.drop_all()
        db.create_all()
 
    # executed after each test
    def tearDown(self):
        os.remove(os.path.join(BASEDIR,TEST_DB))

    def test_token_exchange(self):
        response = self.public_token.create(INSTITUTION_ID, 
                                                INITIAL_PRODUCTS,
                                                TEST_OPTION_TRANSACTION)

        response = methods.token_exchange(self.client, response['public_token'])
        self.assertIn('access_token', response.keys())
        self.assertIn('item_id', response.keys())
        self.assertIn('request_id', response.keys())

    def test_invalid_token_exchange(self):
        response = methods.token_exchange(self.client, "public-sandbox-23a61cc6-be12-4434-a775-b75b1ebc2776")
        self.assertEqual(response,'INVALID_PUBLIC_TOKEN')

    def test_get_accounts(self):
        start_date = "2019-10-01"
        end_date = "2020-11-01"
        access_token = self.get_access_token(None)
        response = methods.get_transactions(self.client, 
                                            start_date, 
                                            end_date,
                                            access_token)
        self.assertEqual(type(response),list)

    def test_get_accounts(self):
        access_token = self.get_access_token(None)
        response = methods.get_accounts(self.client, access_token)

        self.assertEqual(type(response),list)


    def get_access_token(self, options=TEST_OPTION_TRANSACTION):
        response = self.public_token.create(INSTITUTION_ID, 
                                            INITIAL_PRODUCTS,
                                            options)
        response = methods.token_exchange(self.client, 
                                          response['public_token'])
        return response['access_token']



    



 