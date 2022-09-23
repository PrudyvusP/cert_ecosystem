from flask import Markup, flash
from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader
from flask_admin.form.rules import FieldSet
from wtforms.validators import Length, InputRequired

from .markup_formatters import (org_list_formatter,
                                parent_single_formatter,
                                children_list_formatter)
from .master import (CreateRetrieveUpdateModelView,
                     MESSAGE_DEFAULT_FORMATTERS)
from ..extentions import db
from ..forms import validate_future_date
from ..models import Message, Organization
from ..views import forms_placeholders as dictionary

CHOOSE_MAIN_MESSAGE_TEXT = "Выберете письмо-основание"
CHOOSE_MULT_ORG_TEXT = "Выберете организацию (-и)"
FLASH_ERROR = "error"

MESSAGE_DATE_REGISTERED_TEXT = ("Дата подписи не может"
                                " быть позже даты регистрации!")
MESSAGE_INFORMATION_MIN_CONST = 10
MESSAGE_NO_ORG_CHOSEN_TEXT = "Не выбрана организация"
MESSAGE_TYPE_TEXT = "Письмо либо исходящее, либо входящее!"
MESSAGE_VISIBLE_LEN_CONST = 70


class MessageModelView(CreateRetrieveUpdateModelView):
    """View-класс сообщения."""

    def validate_form(self, form) -> bool:
        """Валидация формы на предмет адекватности."""

        if form.data.get('date_approved'):
            date_approved = form.date_approved.data
            date_registered = form.date_registered.data
            date_inbox_approved = form.date_inbox_approved.data
            if date_approved and (date_registered or date_inbox_approved):
                flash(MESSAGE_TYPE_TEXT,
                      category=FLASH_ERROR)
                return False

        if (form.data.get('date_registered')
                and form.data.get('date_inbox_approved')):
            date_registered = form.date_registered.data
            date_inbox_approved = form.date_inbox_approved.data
            if date_registered < date_inbox_approved:
                flash(MESSAGE_DATE_REGISTERED_TEXT,
                      category=FLASH_ERROR)
                return False

        return super().validate_form(form)

    # MAIN options
    can_delete = True

    # LIST options
    column_default_sort = ('datetime_created', True)
    column_descriptions = dictionary.message_fields_descriptions
    column_filters = ['information', 'date_approved', 'our_outbox_number',
                      'date_inbox_approved', 'number_inbox_approved',
                      'organizations.db_name']
    column_formatters = {
        "information": lambda v, c, m, p:
        f"{m.information[:MESSAGE_VISIBLE_LEN_CONST]}..."
        if len(m.information) >= MESSAGE_VISIBLE_LEN_CONST else m.information,
        "organizations": org_list_formatter
    }
    column_formatters_detail = {
        "information": lambda v, c, m, p:
        Markup(m.information.replace('\n', '<br>')),
        "organizations": org_list_formatter,
        "parent": parent_single_formatter,
        "children": children_list_formatter
    }
    column_formatters_export = {
        "information": lambda v, c, m, p: m.information
    }
    column_labels = dictionary.message_fields_labels
    column_labels['organizations.db_name'] = 'Название организации'
    column_list = ['date_approved', 'our_outbox_number',
                   'organizations', 'information', 'date_inbox_approved',
                   'number_inbox_approved', 'date_registered',
                   'our_inbox_number']

    column_searchable_list = ['information',
                              'our_outbox_number',
                              'number_inbox_approved']
    column_sortable_list = ['date_inbox_approved',
                            'date_registered', 'date_approved']
    column_type_formatters = MESSAGE_DEFAULT_FORMATTERS

    # RETRIEVE OPTIONS
    column_details_list = ['organizations', 'is_outgoing',
                           'parent', 'date_inbox_approved',
                           'number_inbox_approved', 'date_registered',
                           'children', 'our_inbox_number', 'date_approved',
                           'our_outbox_number', 'information']
    column_type_formatters_detail = MESSAGE_DEFAULT_FORMATTERS

    # CREATE / UPDATE options
    form_ajax_refs = {
        'organizations': QueryAjaxModelLoader('organizations',
                                              db.session,
                                              Organization,
                                              fields=['db_name'],
                                              filters=['is_active=True'],
                                              order_by='full_name',
                                              placeholder=CHOOSE_MULT_ORG_TEXT,
                                              minimum_input_length=2
                                              ),
        'parent': QueryAjaxModelLoader('parent',
                                       db.session,
                                       Message,
                                       fields=['number_inbox_approved',
                                               'our_inbox_number',
                                               'our_outbox_number'],
                                       order_by='datetime_created',
                                       placeholder=CHOOSE_MAIN_MESSAGE_TEXT,
                                       minimum_input_length=1
                                       )
    }
    form_args = {
        'date_registered': {'validators': [validate_future_date]},
        'date_inbox_approved': {'validators': [validate_future_date]},
        'date_approved': {'validators': [validate_future_date]},
        'information': {'validators': [Length(MESSAGE_INFORMATION_MIN_CONST)]},
        'organizations': {'validators': [
            InputRequired(MESSAGE_NO_ORG_CHOSEN_TEXT)]}
    }
    form_excluded_columns = ('methodical_docs', 'datetime_created',
                             'datetime_updated', 'children')
    form_rules = (
        FieldSet(('organizations',),
                 'Отправитель(-и)/получатель(-и)'),
        FieldSet(('parent', 'our_outbox_number', 'date_approved'),
                 'Исходящее письмо'),
        FieldSet(('our_inbox_number', "date_registered",
                  'number_inbox_approved', 'date_inbox_approved'),
                 'Входящее письмо'),
        FieldSet(('information',),
                 'Содержание письма'),
    )
    form_widget_args = dictionary.message_fields_placeholders
