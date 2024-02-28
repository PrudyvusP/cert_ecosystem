from flask_admin.contrib.sqla import ModelView

from ..utils import create_prefix
from .forms_placeholders import orgadmdoc_fields_labels


class OrgAdmDocModelView(ModelView):
    """View-класс организационно-распорядительного
     документа организации."""
    can_create = True
    can_view_details = False
    can_edit = True
    can_delete = False

    column_list = ['name']
    column_labels = orgadmdoc_fields_labels

    form_excluded_columns = ('name_prefix', 'organization',
                             'date_added', 'date_updated')

    def on_model_change(self, form, model, is_created):
        """Переопределяет создание/изменение модели документа.
         Создает префикс документа по его названию."""
        if is_created:
            model.name_prefix = create_prefix(model.name)
