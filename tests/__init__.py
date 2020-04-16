import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
os.environ['PLAID_CLIENT_ID'] = '***REMOVED***'
os.environ['PLAID_SECRET'] = '***REMOVED***'
os.environ['PLAID_PUBLIC_KEY'] = '***REMOVED***'
os.environ['PLAID_ENV'] = 'sandbox'
