from .markup_formatters import (resp_org_name_formatter, res_name_formatter,
                                cert_name_formatter)
from .master import BaseModelView
from ..views import forms_placeholders as dictionary


class ResponseModelView(BaseModelView):
    """View-класс единицы зоны ответственности."""

    # MAIN options
    can_create = False
    can_edit = False

    # LIST OPTIONS
    column_list = ['resource.org_owner.full_name', 'resource',
                   'date_start', 'date_end', 'props', 'cert',
                   'services']
    column_filters = ['date_start', 'date_end']
    column_formatters = {
        "resource": res_name_formatter,
        "cert": cert_name_formatter,
        "resource.org_owner.full_name": resp_org_name_formatter
    }
    column_formatters_export = {
        "resource": lambda v, c, m, n: m.resource,
        "cert": lambda v, c, m, n: m.cert,
    }
    column_labels = dictionary.response_fields_labels
    column_labels['resource.org_owner.full_name'] = 'Владелец'

    column_sortable_list = ['resource.name', 'date_start', 'date_end',
                            'resource.org_owner.full_name',
                            ('cert', 'cert.name'),
                            ('resource', 'resource.name')]
    column_searchable_list = ['props']

    # RETRIEVE OPTIONS
    column_details_list = ['cert', 'resource', 'services', 'date_start',
                           'date_end', 'type', 'props', 'comment']
