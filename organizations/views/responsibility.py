import os.path

from flask import request, redirect, flash, current_app as app
from flask_admin import expose
from werkzeug.utils import secure_filename

from .markup_formatters import (resp_org_name_formatter, res_name_formatter,
                                cert_name_formatter)
from .master import BaseModelView
from ..filters import RespResourceRegionFilter, RespResourceOkrugFilter
from ..forms import AddXMLForm
from ..models import Region, Okrug
from ..utils import (get_instance_choices, send_mail,
                     get_cur_time, create_zip_archive_mem)
from ..views import forms_placeholders as dictionary
from ..xml_parser import XMLHandler

SEARCH_MODEL_TEXT = 'Рег. № ОКИИ или реквизиты док-та'


class ResponseModelView(BaseModelView):
    """View-класс единицы зоны ответственности."""

    def search_placeholder(self):
        """Переопределяет текст, отображаемый в Поиске."""
        return SEARCH_MODEL_TEXT

    # MAIN options
    can_create = True
    can_edit = False

    # LIST OPTIONS
    column_list = ['resource.org_owner.full_name', 'resource.name',
                   'resource.category', 'resource.fstec_reg_number',
                   'date_start', 'date_end', 'props', 'cert.name',
                   'services']
    column_filters = ['date_start', 'date_end', 'resource.org_owner.full_name',
                      'resource.org_owner.inn', 'cert.name',
                      'cert.org_owner.full_name', 'resource.name',
                      'resource.is_okii', 'resource.category']
    column_select_related_list = ['resource', 'cert', 'resource.org_owner']
    column_formatters = {
        "resource.name": res_name_formatter,
        "cert.name": cert_name_formatter,
        "resource.org_owner.full_name": resp_org_name_formatter
    }
    column_formatters_export = {
        "resource.name": lambda v, c, m, n: m.resource,
        "cert.name": lambda v, c, m, n: m.cert,
    }
    column_labels = dictionary.response_fields_labels
    column_labels.update({
        'resource.org_owner.full_name':
            dictionary.resource_fields_description['org_owner'],
        'resource.org_owner.inn': 'ИНН владельца ресурса',
        'resource.fstec_reg_number':
            dictionary.resource_fields_description['fstec_reg_number'],
        'resource.is_okii': dictionary.resource_fields_description['is_okii'],
        'resource.category':
            dictionary.resource_fields_description['category'],
        'resource.name': dictionary.resource_fields_description['name'],
        'cert.name': dictionary.cert_fields_labels['name'],
        'cert.org_owner.full_name': dictionary.cert_fields_labels['org_owner']
    })

    column_sortable_list = ['resource.name', 'date_start', 'date_end',
                            'resource.org_owner.full_name',
                            'resource.category', 'cert.name',
                            'resource.name']
    column_searchable_list = ['props', 'resource.fstec_reg_number',
                              'resource.org_owner.db_name']

    # RETRIEVE OPTIONS
    column_details_list = ['cert.name', 'resource.name', 'services',
                           'date_start', 'date_end', 'type', 'props',
                           'comment']

    @expose('/')
    def index_view(self):
        """Расширяет view-класс для возможности обновления
         динамических фильтров."""
        self.dynamic_filters = []
        self.dynamic_filters.extend(
            [
                RespResourceRegionFilter(
                    None,
                    name='Регион(-ы) расположения ресурса',
                    options=get_instance_choices(Region,
                                                 'region_id',
                                                 'name')
                ),
                RespResourceOkrugFilter(
                    None,
                    name='Округ(-а) расположения ресурса',
                    options=get_instance_choices(Okrug,
                                                 'okrug_id',
                                                 'name')
                ),
            ]
        )
        self._refresh_filters_cache()
        return super(ResponseModelView, self).index_view()

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        """Переопределяет метод создания сущности Responsibility."""

        form = AddXMLForm()
        form.submit.label.text = "Загрузить"
        if form.validate_on_submit() and request.method == 'POST':
            files = request.files.getlist("files")
            email = form.email.data
            log_names = []
            if not all([file.mimetype == 'text/xml' for file in files]):
                flash('Убедитесь, что выбраны файлы с расширением .xml',
                      category="error")
                return redirect(request.url)

            cur_time = get_cur_time()

            for file in files:
                file_name = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_PATH'], file_name)

                try:
                    file.save(file_path)
                except OSError:
                    flash('Не удалось сохранить файл(-ы)',
                          category="error")
                    return redirect(request.url)

                log_file_name = f'{file_path}-{cur_time}.log'
                handler = XMLHandler(
                    file=file_path, schema=app.config['SCHEMA_PATH'],
                    logger_file=log_file_name, logger_name=file_name)
                handler.handle()
                log_names.append(log_file_name)
            archive = create_zip_archive_mem(log_names)
            archive_name = f'{cur_time}-results.zip'
            to = app.config['BOSS_EMAIL_FOR_NOTIFY']

            if email not in to:
                to.append(email)

            send_mail(
                user=app.config['SMTP_USER'],
                password=app.config['SMTP_PASSWORD'],
                send_to=to,
                subject='CERT-ECOSYSTEM - результаты загрузки XML-файла',
                text='Направляю результаты загрузки XML-файла',
                host=app.config['SMTP_HOST'],
                port=app.config['SMTP_PORT'],
                file_binary=archive,
                file_binary_name=archive_name
            )

        return self.render('admin/resp_create.html', form=form)
