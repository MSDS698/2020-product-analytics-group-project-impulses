import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"]
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = os.urandom(24)

# for running sphinx documentation:
# class Config(object):
#     SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
#     SQLALCHEMY_TRACK_MODIFICATIONS = True
#     SECRET_KEY = os.urandom(24)
