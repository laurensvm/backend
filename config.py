import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{user}:{passwd}@{host}:3306/{db}'.format(
    #     user=os.environ["DB_USERNAME"],
    #     passwd=os.environ["DB_PASSWORD"],
    #     host=os.environ["DB_HOST"],
    #     db=os.environ["DB_DATABASE"]
    # )

    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(os.path.join(basedir, "app.db"))
    BASEPATH = "data/"
    IMAGE_PATH = "data/ios/photos/"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = [os.environ.get('ADMIN')] or ['theexission@gmail.com']
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'Laurens'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'passwd01'
    ADMIN_EMAIL = "theexission@gmail.com"