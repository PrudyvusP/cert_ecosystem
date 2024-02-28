import os
from pathlib import Path

from celery.schedules import crontab
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))


class Config:
    """Базовые настройки приложения."""

    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')

    BABEL_DEFAULT_LOCALE = 'ru'
    FLASK_ADMIN_FLUID_LAYOUT = True
    FLASK_ADMIN_SWATCH = 'journal'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024

    STATIC_PATH = os.path.join(BASE_DIR, 'static')
    TEMPLATES_PATH = os.path.join(BASE_DIR, 'templates')
    UPLOAD_PATH = os.path.join(BASE_DIR, STATIC_PATH, 'uploads')

    BUSINESS_LOGIC = {
        "DOCX_TEMPLATE_PATH": os.environ.get('DOCX_TEMPLATE_PATH'),
        "EGRUL_SERVICE_URL": os.environ.get(
            'EGRUL_SERVICE_URL', 'http://localhost:28961/'),
        "ORG_FILES_DIR": os.path.join(
            BASE_DIR, STATIC_PATH, 'organizations'),
        "METHOD_DOCS_PATH": os.environ.get('METHOD_DOCS_PATH', '/tmp/'),
        "XSD_SCHEMA_PATH": os.path.join(UPLOAD_PATH, 'CERT-ZONE-DATA-v-00.xsd')
    }

    EMAIL = {
        "HOST": os.environ.get('SMTP_HOST', 'localhost'),
        "PORT": os.environ.get('SMTP_PORT', 25),
        "USER": os.environ.get('SMTP_USER'),
        "PASSWORD": os.environ.get('SMTP_PASSWORD'),
        "BOSS_EMAIL_FOR_NOTIFY": os.environ.get(
            'BOSS_EMAIL_FOR_NOTIFY').split(',')
    }

    CELERY = {
        "broker_url": os.environ.get('CELERY_BROKER_URL',
                                     'pyamqp://localhost'),
        "result_backend": None,
        "task_ignore_result": True,
        "timezone": "Europe/Moscow",
        "beat_schedule":
            {
                "notify-every-mon-wed-fri-8-30": {
                    "task": "organizations.tasks.send_notify_email",
                    "schedule": crontab(hour=8, minute=30,
                                        day_of_week=[1, 3, 5]),
                }}
    }


class ProdConfig(Config):
    """Настройки для продакшена."""

    DB_HOST = os.environ.get('DB_HOST')
    DB_NAME = os.environ.get('DB_NAME')
    DB_PORT = os.environ.get('DB_PORT')
    POSTGRES_USER = os.environ.get('POSTGRES_USER')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')

    SQLALCHEMY_DATABASE_URI = ('postgresql+psycopg2://'
                               f'{POSTGRES_USER}:{POSTGRES_PASSWORD}'
                               f'@{DB_HOST}:{DB_PORT}/{DB_NAME}')


class DevConfig(Config):
    """Настройки для разработки."""

    DEBUG = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    SQLALCHEMY_DATABASE_URI = ('sqlite:///'
                               + os.path.join(BASE_DIR,
                                              'data.db')
                               )


class TestConfig(Config):
    """Настройки для тестирования."""

    SQLALCHEMY_DATABASE_URI = ('sqlite:///'
                               + os.path.join(BASE_DIR,
                                              'test_data.db')
                               )
