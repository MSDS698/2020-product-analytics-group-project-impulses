import os
import unittest
from test_setup import TestSetup
from app import classes, db


# TEST_DB = 'test.db'
# BASEDIR = os.path.abspath(os.path.dirname(__file__))
# os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'\
#                                         + os.path.join(BASEDIR, TEST_DB)

# from app import application, classes, db


class TestDB(TestSetup):
    # """Class for testing the database"""
    #
    # def setUp(self):
    #     """Initialization for the test cases.
    #
    #     This is executed prior to each test.
    #     """
    #     application.config['TESTING'] = True
    #     application.config['WTF_CSRF_ENABLED'] = False
    #     application.config['DEBUG'] = False
    #     self.app = application.test_client()
    #     db.drop_all()
    #     db.create_all()
    #
    # def tearDown(self):
    #     """Clean-up for the test cases.
    #
    #     This is executed after each test.
    #     """
    #     #os.remove(os.path.join(BASEDIR, TEST_DB))
    #     pass

    # Tests
    def test_user(self):
        """Test if the user class is functioning"""
        test_user = classes.User("first", "last", "xxx@gmail.com",
                                 "1234789213", "password")
        db.session.add(test_user)
        db.session.commit()

        user = classes.User.query.first()
        self.assertEqual(user.first_name, "first", msg="check first name")
        self.assertEqual(user.last_name, "last", msg="check last name")
        self.assertEqual(user.email, "xxx@gmail.com", msg="check email")
        self.assertEqual(user.phone, "1234789213", msg="check phone number")
        self.assertTrue(user.check_password, msg="check password")

if __name__ == "__main__":
    unittest.main()