from os import environ, path

from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class Config:
    """Базовые настройки приложения."""

    DEBUG = False
    SECRET_KEY = environ.get('SECRET_KEY')

    BABEL_DEFAULT_LOCALE = 'ru'
    FLASK_ADMIN_FLUID_LAYOUT = True
    FLASK_ADMIN_SWATCH = 'cerulean'

    BASE_DIR = basedir
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    DIR_WITH_ORG_FILES = path.join(
        BASE_DIR,
        STATIC_FOLDER,
        'organizations'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAX_CONTENT_LENGTH = 100 * 1024 * 1024

    EGRUL_SERVICE_URL = environ.get('EGRUL_SERVICE_URL',
                                    'http://localhost:28961')


class ProdConfig(Config):
    """Настройки для продакшена."""

    DB_HOST = environ.get('DB_HOST')
    DB_NAME = environ.get('DB_NAME')
    DB_PORT = environ.get('DB_PORT')
    POSTGRES_USER = environ.get('POSTGRES_USER')
    POSTGRES_PASSWORD = environ.get('POSTGRES_PASSWORD')

    SQLALCHEMY_DATABASE_URI = ('postgresql+psycopg2://'
                               f'{POSTGRES_USER}:{POSTGRES_PASSWORD}'
                               f'@{DB_HOST}:{DB_PORT}/{DB_NAME}')


class DevConfig(Config):
    """Настройки для разработки."""

    DEBUG = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    SQLALCHEMY_DATABASE_URI = ('sqlite:///'
                               + path.join(basedir,
                                           '../data.db')
                               )


class TestConfig(Config):
    """Настройки для тестирования."""

    SQLALCHEMY_DATABASE_URI = ('sqlite:///'
                               + path.join(basedir,
                                           '../test_data.db')
                               )
