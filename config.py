import os.path
from os import environ, path

from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class Config:
    """Базовые настройки приложения."""
    BABEL_DEFAULT_LOCALE = 'ru'
    BASE_DIR = basedir
    DEBUG = True
    FLASK_ADMIN_FLUID_LAYOUT = True
    FLASK_ADMIN_SWATCH = 'cerulean'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    SECRET_KEY = environ.get('SECRET_KEY')

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_FOLDER = 'static'

    TEMPLATES_FOLDER = 'templates'


class ProdConfig(Config):
    """Настройки для продакшена."""
    FLASK_ENV = 'production'
    DEBUG = False
    SQLALCHEMY_ECHO = False
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
    FLASK_ENV = 'development'
    SQLALCHEMY_DATABASE_URI = ('sqlite:///' +
                               os.path.join(basedir, 'data.db'))


class TestConfig(Config):
    """Настройки для тестирования."""
    FLASK_ENV = 'testing'
    TESTING = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = ('sqlite:///' +
                               os.path.join(basedir, 'test_data.db'))
