import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # local testing
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')
    # development
    SQLALCHEMY_DATABASE_URI = 'postgresql://masteruser:productimpulses@maindb.cuwtgivgs05r.us-west-1.rds.amazonaws.com/impulses_dev'
    # # production
    # SQLALCHEMY_DATABASE_URI = 'postgresql://masteruser:productimpulses@maindb.cuwtgivgs05r.us-west-1.rds.amazonaws.com/impulses_prod'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = os.urandom(24)