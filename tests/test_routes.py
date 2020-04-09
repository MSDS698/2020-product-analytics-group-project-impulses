import os
import unittest
import flask

TEST_DB = 'test.db'
BASEDIR = os.path.abspath(os.path.dirname(__file__))
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' \
                                        + os.path.join(BASEDIR, TEST_DB)

from app import application, classes, db


class TestRoutes(unittest.TestCase):
    """Class for testing the routes"""

    def setUp(self):
        """Initialization for the test cases

        This is executed prior to each test.
        """
        application.config['TESTING'] = True
        application.config['WTF_CSRF_ENABLED'] = False
        application.config['DEBUG'] = False
        self.app = application.test_client()
        db.drop_all()
        db.create_all()

    def tearDown(self):
        """Clean-up for the test cases

        This is executed after each test.
        """
        db.session.remove()
        os.remove(os.path.join(BASEDIR, TEST_DB))

    ####################################################################
    # Route Tests
    ####################################################################
    def test_main_page_not_logged_in(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_valid_login(self):
        # add user to db
        test_user = classes.User('First', 'Last', 'test@test.com',
                                 '6158675309', 'password')
        db.session.add(test_user)
        db.session.commit()
        with self.app as c:
            email = 'test@test.com'
            password = 'password'
            response = self.app.post(
                '/login',
                data=dict(email=email, password=password),
                follow_redirects=True
            )
            is_logged_in = '_user_id' in flask.session
        self.assertEqual(is_logged_in, True)

    def test_invalid_login(self):
        # add user to db
        test_user = classes.User('First', 'Last', 'test@test1.com',
                                 '6158172309', 'password')
        db.session.add(test_user)
        db.session.commit()
        with self.app as c:
            email = 'test@test.com'
            password = 'wrong_password'
            response = self.app.post(
                '/login',
                data=dict(email=email, password=password),
                follow_redirects=True
            )
            is_logged_in = '_user_id' in flask.session
        self.assertEqual(is_logged_in, False)

    def test_valid_register(self):
        # add user to db
        data = {'first_name': 'First',
                'last_name': 'Last',
                'email': 'test@test.com',
                'phone': '1234567890',
                'password': 'password'}
        with self.app as c:
            response = self.app.post('/register', data=data)
            self.assertTrue(response.location.endswith('login'))

    def test_email_exists_register(self):
        test_user = classes.User('First', 'Last', 'test@test.com',
                                 '6158172309', 'password')
        db.session.add(test_user)
        db.session.commit()
        data = {'first_name': 'First',
                'last_name': 'Last',
                'email': 'test@test.com',
                'phone': '1234567890',
                'password': 'password'}
        with self.app as c:
            response = self.app.post('/register', data=data)
            # When location is None then no redirect happens
            self.assertEqual(response.location, None)

    def test_phone_exists_register(self):
        test_user = classes.User('First', 'Last', 'test@test.com',
                                 '6158172309', 'password')
        db.session.add(test_user)
        db.session.commit()
        data = {'first_name': 'First',
                'last_name': 'Last',
                'email': 'test@test1.com',
                'phone': '6158172309',
                'password': 'password'}
        with self.app as c:
            response = self.app.post('/register', data=data)
            self.assertEqual(response.location, None)


if __name__ == "__main__":
    unittest.main()
