# config.py
import os
basedir = os.path.abspath((os.path.dirname(__file__)))

class BaseConfig(object):
    DEBUG = True
    SECRET_KEY = '\x1c\x0fws\xfd=\xeb\xc1\x03\xaf*\xa40\xab\xe8\xaf\xb4*\x8a\xa3\xf6\xfd\x14\xfd'
    SQLALCHEMY_DATABASE_URI = 'mysql://username:password@localhost/mitdb'

    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #     'sqlite:///' + os.path.join(basedir, 'app.db')

    SECURITY_PASSWORD_SALT = 'bcrypt'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # FLASK_APP=run.py

    USERNAME = 'ablie'
    PASSWORD = 'ablie'


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False


app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
