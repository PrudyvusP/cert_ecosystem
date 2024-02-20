import re

import requests
from flask import current_app as app, flash, redirect, request, url_for
from flask_admin import BaseView, expose

from ..extentions import db
from ..models import Organization, Region
from ..utils import (INN_PATTERN, KPP_PATTERN, OGRN_PATTERN, get_api_url,
                     check_response, check_retrieve_response,
                     convert_from_json_to_dict,
                     )


def guess_search_term(term: str) -> dict:
    """Возвращает параметр фильтрации по типу <term>."""
    term = term.strip()
    if not term.isdigit():
        return {"q": term, "url": "fts-search/"}

    if re.match(INN_PATTERN, term):
        return {"inn": term}
    if re.match(OGRN_PATTERN, term):
        return {"ogrn": term}
    if re.match(KPP_PATTERN, term):
        return {"kpp": term}


class WorkspaceView(BaseView):
    """View-класс рабочего пространства."""

    def is_visible(self) -> bool:
        return False

    @expose('/', methods=['POST'])
    def egrul_search(self):
        """Описание view-функции поиска сведений в ЕГРЮЛ."""
        prev_url = request.form.get('prev_url')
        search_keyword = request.form['search_keyword']
        url = (request.form.get('next_page')
               or request.form.get('prev_page')
               or get_api_url('api/organizations/')
               )

        params = guess_search_term(search_keyword)
        url += params.pop('url', '')

        try:
            _request = requests.get(url, params=params)
        except requests.exceptions.RequestException:
            app.logger.error('EGRUL API не доступен')
            flash(
                category='error',
                message=('Поиск по ЕГРЮЛ в настоящий момент недоступен,'
                         ' администратор уже оповещен и скоро починит!')
            )
            return redirect(prev_url)
        response = convert_from_json_to_dict(_request)

        count = 0
        found_organizations = []

        if response:
            found_organizations = check_response(response)
            count = response['count']
            prev_page = response['previous']
            next_page = response['next']
            date_info = response['date_info']

            for found_organization in found_organizations:
                exists = (
                    db.session.query(Organization)
                    .filter(Organization.full_name == found_organization[
                        'full_name'])
                    .filter(Organization.kpp == found_organization['kpp'])
                    .filter(Organization.inn == found_organization['inn'])
                ).first()
                if exists:
                    found_organization['is_workspace'] = True
                    found_organization['org_id'] = exists.org_id
                else:
                    found_organization['is_workspace'] = False
                    found_organization['org_id'] = None

            return self.render('admin/egrul_search_results.html',
                               count=count,
                               found_organizations=found_organizations,
                               search_keyword=search_keyword,
                               prev_page=prev_page,
                               next_page=next_page,
                               actual_date=date_info)

        return self.render('admin/egrul_search_results.html',
                           count=count,
                           found_organizations=found_organizations,
                           search_keyword=search_keyword)

    @expose('/add/', methods=['POST'])
    def add_to_workspace(self):
        """Описание вью-функции добавления организации
        из ЕГРЮЛ в рабочее пространство."""

        api_url = get_api_url(request.form['org_url'].lstrip('/'))
        _request = requests.get(api_url)
        response = convert_from_json_to_dict(_request)
        response = check_retrieve_response(response)

        new_org = Organization(
            inn=response['inn'],
            kpp=response['kpp'],
            ogrn=response['ogrn'],
            full_name=response['full_name'],
            short_name=response.get("short_name") or response["full_name"],
            factual_address=response['factual_address'],
            region=db.session.query(Region).get(response['region_code'])
        )

        try:
            db.session.add(new_org)
            db.session.commit()
        except Exception as e:
            flash("Не удалось перенести организацию в рабочее пространство",
                  category='error')
            app.logger.error('Ошибка при записи в БД')

        else:
            flash("Организация успешно добавлена", category='success')
        finally:
            return redirect(
                url_for('organizations.details_view', id=new_org.org_id))
