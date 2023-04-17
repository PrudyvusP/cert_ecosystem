from flask import flash, Markup
from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader
from flask_admin.form.rules import FieldSet
from wtforms.validators import Length, InputRequired

from .markup_formatters import (org_list_formatter,
                                parent_single_formatter,
                                children_list_formatter,
                                methodical_docs_formatter)
from .master import BaseModelView
from .system_messages_for_user import (MESSAGE_NO_ORG_CHOSEN_TEXT,
                                       MESSAGE_TYPE_TEXT,
                                       MESSAGE_DATE_REGISTERED_TEXT,
                                       FLASH_ERROR)
from ..extentions import db
from ..filters import MessageIsMethodDoc
from ..forms import validate_future_date
from ..models import Message, Organization
from ..views import forms_placeholders as dictionary

CHOOSE_MAIN_MESSAGE_TEXT = "Выберете письмо-основание"
CHOOSE_MULT_ORG_TEXT = "Выберете организацию (-и)"

MESSAGE_INFORMATION_MIN_CONST = 10
MESSAGE_VISIBLE_LEN_CONST = 70
SEARCH_MODEL_TEXT = "Любые реквизиты письма"


class MessageModelView(BaseModelView):
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

    create_template = 'admin/msg_create.html'
    edit_template = 'admin/msg_edit.html'

    # LIST options
    column_default_sort = ('datetime_created', True)
    column_descriptions = dictionary.message_fields_descriptions
    column_filters = ['information', 'is_inbox',
                      'date_inbox_approved', 'number_inbox_approved',
                      'date_registered', 'our_inbox_number',
                      'organizations.db_name',
                      'date_approved', 'our_outbox_number',
                      MessageIsMethodDoc(
                          None,
                          'Письмо с методичками?'
                      ),
                      ]
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
        "children": children_list_formatter,
        "methodical_docs": methodical_docs_formatter,
    }
    column_formatters_export = {
        "information": lambda v, c, m, p: m.information,
        "organizations": lambda v, c, m, p:
        Markup(", ".join([organization.full_name
                          for organization in m.organizations]))
    }
    column_labels = dictionary.message_fields_labels
    column_labels['organizations.db_name'] = 'Название организации'
    column_list = ['our_outbox_number', 'date_approved',
                   'organizations', 'information', 'is_inbox',
                   'number_inbox_approved', 'date_inbox_approved',
                   'our_inbox_number', 'date_registered',
                   ]

    column_searchable_list = ['information',
                              'our_outbox_number',
                              'number_inbox_approved',
                              'organizations.db_name',
                              'organizations.short_name']

    def search_placeholder(self):
        """Переопределяет текст, отображаемый в Поиске по модели письма."""
        return SEARCH_MODEL_TEXT

    column_sortable_list = ['date_inbox_approved',
                            'date_registered', 'date_approved']

    # RETRIEVE OPTIONS
    column_details_list = ['organizations', 'is_inbox',
                           'parent', 'date_inbox_approved',
                           'number_inbox_approved', 'date_registered',
                           'children', 'our_inbox_number', 'date_approved',
                           'our_outbox_number', 'information',
                           'methodical_docs']

    # CREATE / UPDATE options
    form_ajax_refs = {
        'organizations': QueryAjaxModelLoader('organizations',
                                              db.session,
                                              Organization,
                                              fields=['db_name', 'short_name'],
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
    form_columns = ('date_registered',
                    'date_inbox_approved',
                    'date_approved',
                    'number_inbox_approved',
                    'information',
                    'our_inbox_number',
                    'our_outbox_number',
                    'organizations',
                    'is_inbox',
                    'parent')

    form_args = {
        'date_registered': {'validators': [validate_future_date]},
        'date_inbox_approved': {'validators': [validate_future_date]},
        'date_approved': {'validators': [validate_future_date]},
        'information': {'validators': [Length(MESSAGE_INFORMATION_MIN_CONST)]},
        'organizations': {'validators': [
            InputRequired(MESSAGE_NO_ORG_CHOSEN_TEXT)]},

    }
    # Спрячем полное описание элементов формы
    for key in form_columns:
        if key in form_args:
            form_args[key]['description'] = ''
        else:
            form_args[key] = {'description': ''}

    form_rules = (
        FieldSet(('is_inbox',), 'Выберете тип письма'),
        FieldSet(('organizations',),
                 'Отправитель(-и)/получатель(-и)'),
        FieldSet(('parent',),
                 'Письмо-основание'),
        FieldSet(('our_outbox_number', 'date_approved'),
                 'Исходящее письмо'),
        FieldSet(('our_inbox_number', "date_registered",
                  'number_inbox_approved', 'date_inbox_approved'),
                 'Входящее письмо'),
        FieldSet(('information',),
                 'Содержание письма'),
    )

    form_widget_args = dictionary.message_fields_placeholders
    date_widget_format = {
        'type': 'date',
        'autocomplete': 'off',
        'data-role': '',
    }
    form_widget_args['is_inbox'] = {'class': 'form-control-lg mx-3',
                                    'style': "transform: scale(2.2)"}

    for date in ['date_registered', 'date_inbox_approved', 'date_approved']:
        form_widget_args[date] = date_widget_format
