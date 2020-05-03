# import os
# import sys
#
#
# sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
#
# from plaid_methods import methods, add_plaid_data
# from app import classes, db
# from plaid.api import sandbox
# from plaid import Client
#
# os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../app/test.db'
# os.environ['PLAID_CLIENT_ID'] = '5e717f8b062e7500146bfedc'
# os.environ['PLAID_SECRET'] = '3a807e1be3a56c9c40378286eb6cb8'
# os.environ['PLAID_PUBLIC_KEY'] = 'fd4fdc88940c3e8ad4bdafc8e1cdb5'
# os.environ['PLAID_ENV'] = 'sandbox'
#
#
# classes.User.query.delete()
# classes.Transaction.query.delete()
# classes.Accounts.query.delete()
# classes.Coin.query.delete()
# classes.Habits.query.delete()
# classes.PlaidItems.query.delete()
# db.session.commit()
#
# client = Client(os.environ['PLAID_CLIENT_ID'],
#                 os.environ['PLAID_SECRET'],
#                 os.environ['PLAID_PUBLIC_KEY'],
#                 os.environ['PLAID_ENV'])
#
#
# class User():
#     def __init__(self, fname, lname, email, phone, password):
#         self.fname = fname
#         self.lname = lname
#         self.email = email
#         self.phone = phone
#         self.password = password
#
#
# class Habit():
#     def __init__(self, habit_name, habit_category, minute,
#                  hour, day_of_week):
#         self.habit_name = habit_name
#         self.habit_category = habit_category
#         self.minute = minute
#         self.hour = hour
#         self.day_of_week = day_of_week
#
#
# def create_dummy_user(user, sandbox_options=None, habits=None):
#
#     user = classes.User(user.fname, user.lname, user.email,
#                         user.phone, user.password)
#     db.session.add(user)
#     public_token = sandbox.PublicToken(client)\
#         .create('ins_109508',
#                 initial_products=['transactions'],
#                 _options=sandbox_options)['public_token']
#     response = methods.token_exchange(client, public_token)
#     plaid = classes.PlaidItems(user=user, item_id=response['item_id'],
#                                access_token=response['access_token'])
#
#     accounts = methods.get_accounts(client, user.plaid_items[0].access_token)
#     checking_account = [
#         account for account in accounts if account['name'] == "Checking"][0]
#     add_plaid_data.add_accounts(
#         [checking_account], user, user.plaid_items[0], commit=False)
#     transactions = methods.get_transactions(
#         client, '2019-10-01', '2019-11-01', plaid.access_token,
#         checking_account['account_id'])
#     print(f"Number of Transactions added: {len(transactions)}")
#     add_plaid_data.add_transactions(transactions, user, user.accounts[0])
#     db.session.commit()
#
#
# kevin = User('Kevin', 'Loftis', 'loftiskg@gmail.com', '6154831195', '12345')
# options_path = os.path.join(os.path.dirname(__file__), 'custom_user_1.json')
# sandbox_options = {'override_username': 'user_custom',
#                    'override_password': open(options_path).read()}
#
# # coffee_habit = Habit("Make Coffee at Home","Coffee", 0,7,'1-5')
#
# create_dummy_user(kevin, sandbox_options)
