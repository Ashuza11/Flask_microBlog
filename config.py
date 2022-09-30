
import os 
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    """Class used to store configuration variables"""

    # For validation Key
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'You-will-never-guess'

    # Data Base configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email notification configurations 
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']

    # Number of posts per a page 
    POST_PER_PAGE = 5

    # App Suported languages 
    LANGUAGES = ['en', 'fr', 'sw']
