import json

import requests
from flask import request
from flask_admin import BaseView, expose
from requests.exceptions import InvalidJSONError


def check_response(response: dict) -> list:
    """Возвращает список организаций."""
    if not isinstance(response, dict):
        raise TypeError("Вернулось что-то странное")
    key_words = ["count", "next", "count", "results"]
    for key_word in key_words:
        if key_word not in response:
            # logger.error(WRONG_FORMAT_RESPONSE)
            raise Exception("В запросе не хватает ключевых слов")

    search_results = response["results"]
    if not isinstance(search_results, list):
        raise TypeError('Вместо списка поиска что-то странное')
    return search_results


class WorkspaceView(BaseView):

    def is_visible(self):
        return False

    @expose('/', methods=['POST'])
    def egrul_search(self):
        search_keyword = request.form['search_keyword']
        url = 'http://localhost/api/organizations/'

        if search_keyword.isdigit():
            params = {"search": search_keyword}
        else:
            params = {"q": search_keyword}
            url += 'fts-search/'

        try:
            r = requests.get(url, params=params)
        except requests.exceptions.RequestException:
            raise Exception('url problems')
            # logger.error(REQUEST_ERROR, exc_info=True)
            # raise ConnectionIssuesError(REQUEST_ERROR)

        try:
            response = r.json()
        except json.JSONDecodeError:
            # logger.error(INVALID_JSON_ERROR)
            raise InvalidJSONError('rofel')

        print(response is True)
        print('-')
        if response:
            found_organizations = check_response(response)
            count = response['count']
            print(found_organizations)
            print(response['next'])
            print(response['previous'])
        else:
            count = 0

        return self.render('admin/egrul_search_results.html',
                           count=count,
                           found_organizations=found_organizations)
