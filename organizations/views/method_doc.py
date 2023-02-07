import zipfile
from datetime import date
from http import HTTPStatus
from io import BytesIO

from flask import abort, send_file
from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from flask_wtf.file import FileField

from .forms_placeholders import methoddoc_fields_labels
from ..extentions import db
from ..models import MethodicalDoc
from ..utils import create_prefix

NOT_PDF_MIMETYPE_MSG = "Файл должен иметь разрешение .pdf"
PDF_MIMETYPE_CONST = "application/pdf"


class MethodDocModelView(ModelView):
    """View-класс методического документа."""
    can_create = True
    can_view_details = False
    can_edit = True
    can_delete = True

    # TODO запретить удаление перед продом!
    # can_delete = False

    column_labels = methoddoc_fields_labels
    column_list = ('name', 'date_approved', 'props',
                   'is_conf', 'is_active',
                   'date_added', 'date_updated')
    column_exclude_list = ('data', 'path_prefix')
    column_default_sort = ('name')
    list_template = 'admin/method-doc_list.html'

    form_excluded_columns = ('messages', 'date_added', 'date_updated',
                             'path_prefix', 'data')

    form_extra_fields = {
        'pdf': FileField('PDF-образ')
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
        file = form.pdf.data
        if file:
            if file.mimetype == PDF_MIMETYPE_CONST:
                model.data = form.pdf.data.read()
            else:
                return abort(HTTPStatus.BAD_REQUEST,
                             NOT_PDF_MIMETYPE_MSG)

    @expose('/<int:method_doc_id>/')
    def get_method_doc_file(self, method_doc_id: int):
        """Возвращает pdf-образ методического документа
         по его <method_doc_id>."""
        method_doc = (db.session
                      .query(MethodicalDoc)
                      .get_or_404(method_doc_id)
                      )
        return send_file(method_doc.get_pdf_file,
                         attachment_filename=method_doc.get_pdf_file_name,
                         as_attachment=True)

    @expose('/get_docs/')
    def get_all_method_docs(self):
        """Возвращает zip-архив с pdf-образами
        всех методических документов."""
        archive_name = f'{date.today()}-methodical-docs-archive.zip'
        memory_archive = BytesIO()
        method_docs = db.session.query(MethodicalDoc).all()

        with zipfile.ZipFile(memory_archive, 'w') as zf:
            for method_doc in method_docs:
                data = zipfile.ZipInfo(method_doc.get_pdf_file_name)
                data.compress_type = zipfile.ZIP_DEFLATED
                zf.writestr(data, method_doc.get_pdf_file.read())
        memory_archive.seek(0)
        return send_file(memory_archive,
                         attachment_filename=archive_name,
                         as_attachment=True)
