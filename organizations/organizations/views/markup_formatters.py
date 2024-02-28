from flask import Markup, url_for

from ..models import Organization
from ..utils import create_a_href_string

SYMB_CONST = "—"


def org_list_formatter(view, context, model, name) -> str:
    """Возвращает удобное отображение организаций в таблице."""
    org_data = getattr(model, name)
    if org_data:
        results = []
        if isinstance(org_data, Organization):
            org_full_name = getattr(org_data, "full_name")
            url = url_for("organizations.details_view", id=org_data.org_id)
            return Markup(create_a_href_string(url, org_full_name))
        else:
            for org in org_data:
                url = url_for("organizations.details_view", id=org.org_id)
                full_url = create_a_href_string(url, org.full_name)
                results.append(full_url)
            markup_string = "<br><br>".join(results)
            return Markup(markup_string)
    return SYMB_CONST


def parent_single_formatter(view, context, model, name) -> str:
    """Возвращает удобное отображение письма-родителя в таблице."""
    if model.parent:
        url = url_for('messages.details_view', id=model.parent.message_id)
        full_url = f"<a href={url}>{str(model.parent)}</a>"
        return Markup(full_url)
    return SYMB_CONST


def children_list_formatter(view, context, model, name):
    """Возвращает удобное отображение писем-потомков в таблице."""
    if model.children:
        results = []
        for child in model.children:
            url = url_for('messages.details_view', id=child.message_id)
            full_url = f"<a href={url}>{str(child)}</a>"
            results.append(full_url)
        markup_string = ', '.join(results)
        return Markup(markup_string)
    return SYMB_CONST


def methodical_docs_formatter(view, context, model, name):
    """Возвращает форматированный перечень прикрепленных методических
    рекомендаций к сообщению."""
    if model.methodical_docs:
        results = []
        for row, methodical_doc in enumerate(model.methodical_docs):
            results.append(f'{row + 1}. {methodical_doc.name}')
        markup_string = ';<br>'.join(results)
        return Markup(markup_string)
    return SYMB_CONST


def method_doc_formatter(view, context, model, name) -> str:
    """Возвращает ссылку на скачивание файла документа по названию."""
    url = url_for('method-docs.get_method_doc_file',
                  method_doc_id=model.method_id)
    full_url = f"<a href={url}>{model.name}</a>"
    return Markup(full_url)


def org_name_formatter(view, context, model, name) -> str:
    """Возвращает ссылку на отображение профиля организации по названию."""
    url = url_for('organizations.details_view',
                  id=model.org_id)
    full_url = f"<a href={url}>{model.full_name}</a>"
    return Markup(full_url)


def res_name_formatter(view, context, model, name) -> str:
    """Возвращает ссылку на отображение ресурса по названию."""
    url = url_for('resources.details_view',
                  id=model.resource.resource_id)
    full_url = f"<a href={url}>{model.resource}</a>"
    return Markup(full_url)


def cert_name_formatter(view, context, model, name) -> str:
    """Возвращает ссылку на отображение центра мониторинга по названию."""
    url = url_for('certs.details_view',
                  id=model.cert.cert_id)
    full_url = f"<a href={url}>{model.cert}</a>"
    return Markup(full_url)


def cert_main_name_formatter(view, context, model, name) -> str:
    """Возвращает ссылку на отображение центра мониторинга по названию."""
    url = url_for('certs.details_view',
                  id=model.cert_id)
    full_url = f"<a href={url}>{model.name}</a>"
    return Markup(full_url)


def resp_org_name_formatter(view, context, model, name) -> str:
    """Возвращает ссылку на отображение профиля организации по названию."""
    url = url_for('organizations.details_view',
                  id=model.resource.org_id)
    full_url = f"<a href={url}>{model.resource.org_owner.full_name}</a>"
    return Markup(full_url)
