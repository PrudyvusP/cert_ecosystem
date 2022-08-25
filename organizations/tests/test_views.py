from http import HTTPStatus

from flask import url_for

from organizations.extentions import db
from organizations.models import Organization


def test_home_page(test_client):
    response = test_client.get('/')
    assert response.status_code == HTTPStatus.OK


def test_organizations_page(test_client):
    new_org = Organization(
        full_name='Правительство Важной области',
        db_name='правительствоважнойобласти',
    )
    response_1 = test_client.get(url_for('organization.index_view'))
    assert response_1.status_code == HTTPStatus.OK
    assert new_org.full_name not in response_1.data.decode('utf-8')

    db.session.add(new_org)
    db.session.commit()
    response_2 = test_client.get(url_for('organization.index_view'))
    assert new_org.full_name in response_2.data.decode('utf-8')
    assert response_2.status_code == HTTPStatus.OK
