from datetime import date

from flask_admin.contrib.sqla import ModelView
from flask_admin.model import typefmt

SYMB_CONST = "—"
DEFAULT_PAGE_SIZE_CONST = 20

DATE_DEFAULT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
DATE_DEFAULT_FORMATTERS.update({
    date: lambda f, x: x.strftime("%d-%m-%Y"),
})

MESSAGE_DEFAULT_FORMATTERS = DATE_DEFAULT_FORMATTERS.copy()
MESSAGE_DEFAULT_FORMATTERS.update({
    type(None): lambda view, value: SYMB_CONST if value is None else "",
})


class CreateRetrieveUpdateModelView(ModelView):
    """Базовый view-класс."""

    def __init__(self, model, session,
                 name=None, category=None, endpoint=None,
                 url=None, static_folder=None,
                 menu_class_name=None, menu_icon_type=None,
                 menu_icon_value=None) -> None:
        super().__init__(model, session, name, category, endpoint,
                         url, static_folder, menu_class_name,
                         menu_icon_type, menu_icon_value)
        self.dynamic_filters = None

    def get_filters(self) -> list:
        """Получает динамические фильтры."""
        _dynamic_filters = getattr(self, 'dynamic_filters', None)
        if _dynamic_filters:
            return (super(CreateRetrieveUpdateModelView,
                          self).get_filters() or []
                    ) + _dynamic_filters
        return super(CreateRetrieveUpdateModelView, self).get_filters()

    # crud
    can_create = True
    can_view_details = True
    can_edit = True
    can_delete = False

    # export
    can_export = True
    export_types = ['csv', 'json', 'yaml']

    # pagination
    can_set_page_size = True
    page_size = DEFAULT_PAGE_SIZE_CONST

    # modals
    create_modal = False
    edit_modal = False

    # default formatters
    column_type_formatters = DATE_DEFAULT_FORMATTERS
    column_type_formatters_detail = DATE_DEFAULT_FORMATTERS
