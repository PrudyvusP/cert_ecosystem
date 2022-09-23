import json

import requests
from flask import current_app as app, flash, redirect, request
from flask_admin import BaseView, expose
from requests.exceptions import InvalidJSONError

from ..exceptions import EgrulApiWrongFormatError


def check_response(response: dict) -> list:
    """Возвращает список организаций."""
    if not isinstance(response, dict):
        raise TypeError("Должен быть словарь!")
    key_words = ["count", "next", "count", "results"]
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
        prev_url = request.form['prev_url']
        search_keyword = request.form['search_keyword']
        url = app.config['EGRUL_SERVICE_URL'] + 'api/organizations/'

        if search_keyword.isdigit():
            params = {"search": search_keyword}
        else:
            params = {"q": search_keyword}
            url += 'fts-search/'

        try:
            r = requests.get(url, params=params)
        except requests.exceptions.RequestException:
            app.logger.error('EGRUL API не доступен')
            flash(
                category='error',
                message=('Поиск по ЕГРЮЛ в настоящий момент недоступен,'
                         ' администратор уже оповещен и скоро починит!')
            )
            return redirect(prev_url)

        try:
            response = r.json()
        except json.JSONDecodeError:
            app.logger.error('Ошибка конвертации ответа от EGRUL API!')
            raise InvalidJSONError('Ошибка конвертации ответа от EGRUL API!')

        count = 0
        found_organizations = []

        # TODO нарисовать пагинацию в шаблоне

        if response:
            found_organizations = check_response(response)
            count = response['count']

        return self.render('admin/egrul_search_results.html',
                           count=count,
                           found_organizations=found_organizations)
