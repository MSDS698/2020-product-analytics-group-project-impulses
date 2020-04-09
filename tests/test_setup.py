import os
import unittest
import flask

TEST_DB = 'test.db'
BASEDIR = os.path.abspath(os.path.dirname(__file__))
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(BASEDIR, TEST_DB)

from app import application, classes, db


 


 
class TestSetup(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        application.config['TESTING'] = True
        application.config['WTF_CSRF_ENABLED'] = False
        application.config['DEBUG'] = False
        application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(BASEDIR, TEST_DB)
        self.app = application.test_client()
        db.drop_all()
        db.create_all()
 
    # executed after each test
    def tearDown(self):
        os.remove(os.path.join(BASEDIR,TEST_DB))