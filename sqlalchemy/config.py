"""
SQLAlchemy Configuration
"""


class Config(object):
    SQLALCHEMY_DATABASE_URI = "postgres://masteruser:productimpulses@"\
                + "maindb.cuwtgivgs05r.us-west-1.rds.amazonaws.com/postgres"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
