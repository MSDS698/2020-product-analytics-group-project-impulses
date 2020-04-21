import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
os.environ['PLAID_CLIENT_ID'] = '5e717f8b062e7500146bfedc'
os.environ['PLAID_SECRET'] = '3a807e1be3a56c9c40378286eb6cb8'
os.environ['PLAID_PUBLIC_KEY'] = 'fd4fdc88940c3e8ad4bdafc8e1cdb5'
os.environ['PLAID_ENV'] = 'sandbox'
os.environ['TWILIO_ACCOUNT_SID'] = 'AC615253ee4368fffc5bf0b52bad19f156'
os.environ['TWILIO_AUTH_TOKEN'] = 'c62366a02efd9bb54a99784c1379d9ba'