import json

import requests
from flask import current_app as app, flash, redirect, request, url_for
from flask_admin import BaseView, expose
from requests.exceptions import InvalidJSONError

from ..exceptions import EgrulApiWrongFormatError
from ..extentions import db
from ..models import Organization, Region


def get_api_url(url_to_go: str) -> str:
    """Создает относительный путь адреса EGRUL-сервиса."""
    base_api_url = app.config['EGRUL_SERVICE_URL']
    return base_api_url + url_to_go


def convert_from_json_to_dict(json_data: requests.models.Response) -> dict:
    """Конвертирует ответ из json в dict."""
    try:
        response = json_data.json()
    except json.JSONDecodeError:
        app.logger.error('Ошибка конвертации ответа от EGRUL API!')
        raise InvalidJSONError('Ошибка конвертации ответа от EGRUL API!')
    return response


def check_response(response: dict) -> list:
    """Возвращает список организаций."""
    if not isinstance(response, dict):
        raise TypeError("Должен быть словарь!")
    key_words = ["count", "next", "previous", "results", "date_info"]
    for key_word in key_words:
        if key_word not in response:
            app.logger.error(
                f'отсутствует {key_word} в структуре ответа от API'
            )
            raise EgrulApiWrongFormatError(
                "В запросе не хватает ключевых слов")

    search_results = response["results"]
    if not isinstance(search_results, list):
        raise TypeError('Должен быть список!')
    return search_results


class WorkspaceView(BaseView):
    """View-класс рабочего пространства."""

    def is_visible(self):
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

        if search_keyword.isdigit():
            params = {"search": search_keyword}
        else:
            params = {"q": search_keyword}
            url += 'fts-search/'

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
            actual_date = date_info['actual_date'][:10]

            # TODO Обращаться для каждого объекта в базу - плохо!

            for found_organization in found_organizations:
                exists = (
                    db.session.query(Organization)
                    .filter(Organization.full_name == found_organization['full_name'])
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
                               actual_date=actual_date)
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
        region = db.session.query(Region).get(int(response.pop('region_code')))
        response["region"] = region

        if not response.get("short_name"):
            response["short_name"] = response["full_name"]

        new_org = Organization(**response)
        try:
            db.session.add(new_org)
            db.session.commit()
        except Exception:
            flash("Не удалось перенести организацию в рабочее пространство",
                  category='error')
            app.logger.error('Ошибка при записи в БД')

        else:
            flash("Организация успешно добавлена", category='success')
        finally:
            return redirect(
                url_for('organizations.details_view', id=new_org.org_id))
