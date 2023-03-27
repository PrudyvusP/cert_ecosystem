import zipfile
from datetime import date
from io import BytesIO
from pathlib import Path

from flask import send_file
from flask_admin import expose
from flask_wtf.file import FileField
from wtforms.validators import InputRequired, ValidationError

from .forms_placeholders import methoddoc_fields_labels
from .markup_formatters import method_doc_formatter
from .master import BaseModelView
from .system_messages_for_user import (METHOD_DOC_BASE_FILE_FORMAT_TEXT,
                                       METHODICAL_DOC_FILE_ERROR_MESSAGE)
from ..extentions import db
from ..models import MethodicalDoc
from ..utils import create_prefix


class MethodDocModelView(BaseModelView):
    """View-класс методического документа."""

    can_view_details = False

    can_set_page_size = False

    can_export = False

    column_labels = methoddoc_fields_labels

    column_list = ('name', 'date_approved', 'props',
                   'is_conf', 'is_active',
                   'date_added', 'date_updated')
    column_default_sort = ('is_active', 'name')

    column_formatters = {
        "name": method_doc_formatter
    }
    list_template = 'admin/method-doc_list.html'

    form_excluded_columns = ('messages', 'date_added', 'date_updated',
                             'path_prefix', 'data', 'data_extension')

    form_extra_fields = {
        'file': FileField('Образ загружаемого документа')
    }
    form_args = {
        'short_name': {"validators": [InputRequired()]},
        'name_for_letter': {"validators": [InputRequired()]}
    }
    date_widget_format = {
        'type': 'date',
        'autocomplete': 'off',
        'data-role': '',
    }
    form_widget_args = {'date_approved': date_widget_format}

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.path_prefix = create_prefix(model.name)

        file = form.file.data
        if file:
            extensions = ''.join(Path(file.filename).suffixes)
            if len(extensions) < 1:
                raise ValidationError(
                    METHOD_DOC_BASE_FILE_FORMAT_TEXT
                )
            model.data = file.read()
            model.data_extension = extensions
        db.session.add(model)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise ValidationError(METHODICAL_DOC_FILE_ERROR_MESSAGE)

    @expose('/<int:method_doc_id>/')
    def get_method_doc_file(self, method_doc_id: int):
        """Возвращает образ методического документа
         по его <method_doc_id>."""
        method_doc = (db.session
                      .query(MethodicalDoc)
                      .get_or_404(method_doc_id)
                      )
        return send_file(method_doc.get_file,
                         attachment_filename=method_doc.get_file_name,
                         as_attachment=True)

    @expose('/get_docs/')
    def get_all_method_docs(self):
        """Возвращает zip-архив с образами
        всех методических документов."""
        archive_name = f'{date.today()}-methodical-docs-archive.zip'
        memory_archive = BytesIO()
        method_docs = (db.session
                       .query(MethodicalDoc)
                       .filter(MethodicalDoc.is_active.is_(True))
                       .all()
                       )

        with zipfile.ZipFile(memory_archive, 'w') as zf:
            for method_doc in method_docs:
                data = zipfile.ZipInfo(method_doc.get_file_name)
                data.compress_type = zipfile.ZIP_DEFLATED
                zf.writestr(data, method_doc.get_file.read())
        memory_archive.seek(0)
        return send_file(memory_archive,
                         attachment_filename=archive_name,
                         as_attachment=True)
