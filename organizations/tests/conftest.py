import pytest

from organizations import create_app
from organizations.extentions import db
from organizations.models import Organization


@pytest.fixture(scope='session')
def flask_app():
    app = create_app(config='test')

    client = app.test_client()

    ctx = app.test_request_context()

    ctx.push()

    yield client

    ctx.pop()


@pytest.fixture(scope='session')
def app_with_db(flask_app):
    db.create_all()

    yield flask_app

    db.session.commit()
    db.drop_all()


@pytest.fixture(scope='session')
def app_with_data(app_with_db):
    new_org = Organization(
        full_name='Правительство Важной области',
        short_name='Правительство Важной области'
    )
    organization = Organization
