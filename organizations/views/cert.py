from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader

from .markup_formatters import org_list_formatter, cert_main_name_formatter
from .master import BaseModelView
from ..extentions import db
from ..models import Organization
from ..views import forms_placeholders as dictionary

SEARCH_MODEL_TEXT = "Название центра или его владельца"
CHOOSE_SINGLE_ORG_TEXT = "Выберете организацию"
ORG_OWNER_AJAX_CONST = 3


class CertModelView(BaseModelView):
    """View-класс центра мониторинга."""

    def search_placeholder(self):
        """Переопределяет текст, отображаемый в Поиске по модели центра
        мониторинга."""
        return SEARCH_MODEL_TEXT

    # CRUD
    can_create = False
    can_edit = False

    # LIST options
    column_filters = ['type', ]
    column_formatters = {"org_owner": org_list_formatter,
                         "name": cert_main_name_formatter}
    column_exclude_list = ['date_added', 'date_updated', 'uuid']
    column_labels = dictionary.cert_fields_labels
    column_searchable_list = ['name',
                              'org_owner.db_name',
                              'org_owner.short_name']
    # CREATE/UPDATE options
    form_ajax_refs = {
        'org_owner': QueryAjaxModelLoader(
            'org_owner',
            db.session,
            Organization,
            fields=['db_name', 'short_name'],
            filters=['is_active=True'],
            order_by='full_name',
            placeholder=CHOOSE_SINGLE_ORG_TEXT,
            minimum_input_length=ORG_OWNER_AJAX_CONST)
    }
    form_columns = ('name', 'type', 'org_owner')
    form_excluded_columns = ('date_added', 'date_updated',
                             'uuid', 'date_actual_resp')

    form_widget_args = dictionary.cert_fields_placeholders
