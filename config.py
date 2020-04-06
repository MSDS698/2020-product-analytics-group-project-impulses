import os
from plaid import Client

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"]
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = os.urandom(24)


ENV_VARS = {
    "PLAID_CLIENT_ID": os.environ["PLAID_CLIENT_ID"],
    "PLAID_PUBLIC_KEY": os.environ["PLAID_PUBLIC_KEY"],
    "PLAID_SECRET": os.environ["PLAID_SECRET"],
    "PLAID_ENV": os.environ["PLAID_ENV"]
}

# setup plaid client
client = Client(
    ENV_VARS["PLAID_CLIENT_ID"],
    ENV_VARS["PLAID_SECRET"],
    ENV_VARS["PLAID_PUBLIC_KEY"],
    ENV_VARS["PLAID_ENV"],
)