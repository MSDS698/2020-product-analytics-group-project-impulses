from app import application, classes, db
import os
import unittest
from datetime import datetime

TEST_DB = 'test.db'
BASEDIR = os.path.abspath(os.path.dirname(__file__))
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' \
                                        + os.path.join(BASEDIR, TEST_DB)


class TestDB(unittest.TestCase):
    """Class for testing the database"""

    def setUp(self):
        """Initialization for the test cases

        This is executed prior to each test.
        """
        application.config['TESTING'] = True
        application.config['WTF_CSRF_ENABLED'] = False
        application.config['DEBUG'] = False
        db.drop_all()
        db.create_all()

    def tearDown(self):
        """Clean-up for the test cases

        This is executed after each test.
        """
        db.session.remove()
        os.remove(os.path.join(BASEDIR, TEST_DB))

    ####################################################################
    # Database Tests
    ####################################################################
    def test_insertion(self):
        """Test if new records can be correctly inserted to each table

        Tables include user, plaid_items, accounts, transaction,
        savings_history and habits.
        """
        # add a new user to user table
        test_user = classes.User(first_name="first", last_name="last",
                                 email="test@gmail.com", phone="9876543210",
                                 password="password")
        db.session.add(test_user)
        db.session.commit()

        # test if the new user is correctly inserted
        user = classes.User.query.first()
        self.assertEqual(user.first_name, "first", msg="check first name")
        self.assertEqual(user.last_name, "last", msg="check last name")
        self.assertEqual(user.email, "test@gmail.com", msg="check email")
        self.assertEqual(user.phone, "9876543210", msg="check phone number")
        self.assertTrue(user.check_password, msg="check password")

        # add a new plaid item to plaid_items table
        test_item = classes.PlaidItems(user_id=user.id, item_id="%item$",
                                       access_token="$token&")
        db.session.add(test_item)
        db.session.commit()

        # test if the new plaid item is correctly inserted
        item = classes.PlaidItems.query.first()
        self.assertEqual(item.user_id, user.id, msg="check user id")
        self.assertEqual(item.item_id, "%item$", msg="check item id")
        self.assertEqual(item.access_token, "$token&",
                         msg="check access token")

        # add a new account to accounts table
        test_account = classes.Accounts(user_id=user.id, plaid_id=item.id,
                                        account_plaid_id="test-account",
                                        account_name="test-bank",
                                        account_type="test-type",
                                        account_subtype="test-subtype")
        db.session.add(test_account)
        db.session.commit()

        # test if the new account is correctly inserted
        account = classes.Accounts.query.first()
        self.assertEqual(account.user_id, user.id, msg="check user id")
        self.assertEqual(account.plaid_id, item.id, msg="check plaid item id")
        self.assertEqual(account.account_plaid_id, "test-account",
                         msg="check account plaid id")
        self.assertEqual(account.account_name, "test-bank",
                         msg="check account name")
        self.assertEqual(account.account_type, "test-type",
                         msg="check account type")
        self.assertEqual(account.account_subtype, "test-subtype",
                         msg="check account subtype")

        # add a new transaction to transaction table
        test_trans = classes.Transaction(user_id=user.id,
                                         account_id=account.id,
                                         trans_amount=123.45,
                                         category_id=12345678,
                                         is_preferred_saving="Yes",
                                         trans_date=datetime.strptime(
                                             "2020-01-01", "%Y-%m-%d"),
                                         post_date=datetime.strptime(
                                             "2020-01-02", "%Y-%m-%d"),
                                         merchant_category="Food",
                                         merchant_address="23 Street",
                                         merchant_city="San Francisco",
                                         merchant_state="CA",
                                         merchant_country="US",
                                         merchant_postal_code="94102",
                                         merchant_longitude="34.12",
                                         merchant_latitude="102.45")
        db.session.add(test_trans)
        db.session.commit()

        # test if the new transaction is correctly inserted
        trans = classes.Transaction.query.first()
        self.assertEqual(trans.user_id, user.id, msg="check user id")
        self.assertEqual(trans.account_id, account.id, msg="check account id")
        self.assertEqual(str(trans.trans_amount), "123.45",
                         msg="check transaction amount")
        self.assertEqual(trans.category_id, 12345678, msg="check category id")
        self.assertEqual(trans.is_preferred_saving, "Yes",
                         msg="check if it is a preferred saving category")
        self.assertEqual(datetime.strftime(trans.trans_date, "%Y-%m-%d"),
                         "2020-01-01", msg="check transaction date")
        self.assertEqual(datetime.strftime(trans.post_date, "%Y-%m-%d"),
                         "2020-01-02", msg="check post date")
        self.assertEqual(trans.merchant_category, "Food",
                         msg="check merchant category")
        self.assertEqual(trans.merchant_address, "23 Street",
                         msg="check merchant address")
        self.assertEqual(trans.merchant_city, "San Francisco",
                         msg="check merchant city")
        self.assertEqual(trans.merchant_state, "CA",
                         msg="check merchant state")
        self.assertEqual(trans.merchant_country, "US",
                         msg="check merchant country")
        self.assertEqual(trans.merchant_postal_code, "94102",
                         msg="check merchant postal code")
        self.assertEqual(trans.merchant_longitude, "34.12",
                         msg="check merchant longitude")
        self.assertEqual(trans.merchant_latitude, "102.45",
                         msg="check merchant latitude")

        # add a new saving history to savings_history table
        test_saving = classes.SavingsHistory(user_id=user.id,
                                             savings_amount="3.21",
                                             total_savings="5.67",
                                             predicted_savings="10.89",
                                             transfer_date=datetime.strptime(
                                                 "2020-02-01", "%Y-%m-%d"),
                                             update_date=datetime.strptime(
                                                 "2020-02-02", "%Y-%m-%d"))
        db.session.add(test_saving)
        db.session.commit()

        # test if the new saving history is correctly inserted
        saving = classes.SavingsHistory.query.first()
        self.assertEqual(saving.user_id, user.id, msg="check user id")
        self.assertEqual(str(saving.savings_amount), "3.21",
                         msg="check savings amount")
        self.assertEqual(str(saving.total_savings), "5.67",
                         msg="check total savings")
        self.assertEqual(str(saving.predicted_savings), "10.89",
                         msg="check predicted savings")
        self.assertEqual(datetime.strftime(saving.transfer_date, "%Y-%m-%d"),
                         "2020-02-01", msg="check transfer date")
        self.assertEqual(datetime.strftime(saving.update_date, "%Y-%m-%d"),
                         "2020-02-02", msg="check update date")

        # add a new habit to habits table
        test_habit = classes.Habits(user_id=user.id, habit_name="coffee",
                                    habit_category="test-category",
                                    time_minute="25",
                                    time_hour="10",
                                    time_day_of_week="2")
        db.session.add(test_habit)
        db.session.commit()

        # test if the new habit is correctly inserted
        habit = classes.Habits.query.first()
        self.assertEqual(habit.user_id, user.id, msg="check user id")
        self.assertEqual(habit.habit_name, "coffee", msg="check habit name")
        self.assertEqual(habit.habit_category, "test-category",
                         msg="check habit category")
        self.assertEqual(habit.time_minute, "25", msg="check habit minute")
        self.assertEqual(habit.time_hour, "10", msg="check habit hour")
        self.assertEqual(habit.time_day_of_week, "2",
                         msg="check habit day of week")


if __name__ == "__main__":
    unittest.main()
