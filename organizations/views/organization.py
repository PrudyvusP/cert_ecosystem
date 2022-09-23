import os
from datetime import date
from http import HTTPStatus

from flask import abort, flash, redirect, send_file, url_for, current_app
from flask_admin import expose
from flask_admin.form.rules import FieldSet
from wtforms.validators import Optional

from .master import CreateRetrieveUpdateModelView
from ..exceptions import (OrgFileNotSavedError, DirNotCreatedError,
                          OrgPDFNotCreatedError)
from ..extentions import db
from ..filters import (OrgRegionFilter,
                       OrgHasAgreementFilter, OrgIsSubjectKIIFilter,
                       OrgHasHadAnyContactsWithUsFilter, OrgDocumentsFilter)
from ..forms import (AddSubjectDocumentForm, validate_future_date,
                     validate_inn, validate_ogrn)
from ..models import (Organization, Region, OrgAdmDoc,
                      OrgAdmDocOrganization)
from ..utils import (create_pdf, create_dot_pdf,
                     get_alpha_num_string)
from ..utils import get_instance_choices
from ..views import forms_placeholders as dictionary

DIR_NOT_CREATED_MSG = "Главная директория организаций не создалась"
BASE_PDF_NOT_CREATED_MSG = "Базовый pdf-файл не смог создаться"
FILE_NOT_CREATED_MSG = "Образ документа не смог сохраниться"
FILENAME_CONST = 20

NOT_PDF_MIMETYPE_MSG = "Not PDF!"
ORGADM_DOC_NAME_CONST = 80
PDF_MIMETYPE_CONST = "application/pdf"
SUCCESS_DATA_UPLOAD_MSG = "Данные успешно добавлены"


class OrganizationModelView(CreateRetrieveUpdateModelView):
    """View-класс организации."""

    def on_model_change(self, form, model, is_created) -> None:
        """Переопределяет поведение создания и изменения организации.
        Создает строку для поиска из полного наименования организации."""
        if model.full_name:
            model.db_name = get_alpha_num_string(model.full_name)

    def get_details_grouped(self) -> dict:
        """Создает сгруппированный словарь данных для
         удобного отображения сведений об организации."""
        return dictionary.get_beautiful_org_formatter(self)

    # MAIN options
    column_export_exclude_list = ['uuid', 'org_id', 'db_name',
                                  'date_added', 'is_gov', 'is_military',
                                  'date_updated', 'is_active']

    # LIST options
    list_template = 'admin/org_list.html'

    column_default_sort = [('full_name', False), ('inn', False)]
    column_descriptions = dictionary.organization_fields_descriptions
    column_editable_list = ['contacts']
    column_exclude_list = ['short_name', 'uuid', 'id', 'date_added',
                           'date_updated', 'region_id', 'ogrn', 'db_name',
                           'agreement_unit', 'boss_fio', 'is_gov',
                           'boss_position', 'factual_address',
                           'is_military']
    column_filters = ('db_name',
                      OrgHasHadAnyContactsWithUsFilter(
                          Organization,
                          'Наличие взаимодействия'
                      ),
                      OrgHasAgreementFilter(
                          Organization.date_agreement,
                          'Соглашение о сотрудничестве'
                      ),
                      OrgIsSubjectKIIFilter(
                          Organization,
                          'Субъект КИИ'
                      ))
    column_formatters_export = dict(
        is_gov=lambda v, c, m, p: '+' if m.is_gov is True else '-',
        is_military=lambda v, c, m, p: '+' if m.is_military is True else '-',
        is_active=lambda v, c, m, p: '+' if m.is_active is True else '-')

    column_labels = dictionary.organization_fields_labels
    column_searchable_list = ['db_name', 'inn']
    column_sortable_list = ('full_name', ('region', 'region.name'),
                            'date_agreement', 'is_gov', 'is_military', 'inn')

    # RETRIEVE OPTIONS
    details_template = 'admin/org_details.html'
    details_columns_grouped = get_details_grouped
    details_grouped = True
    column_details_list = ('full_name', 'short_name', 'inn', 'ogrn',
                           'factual_address', 'region',
                           'boss_position', 'boss_fio', 'contacts',
                           'date_agreement', 'agreement_unit', 'is_gov',
                           'is_military', 'is_subject_kii',
                           'uuid', 'date_added', 'date_updated')

    # CREATE / UPDATE options
    form_args = {"date_agreement": {"validators": [validate_future_date]},
                 "inn": {"validators": [Optional(), validate_inn]},
                 "ogrn": {"validators": [Optional(), validate_ogrn]}}
    form_excluded_columns = ('resources', 'responsible_unit', 'db_name',
                             'messages', 'org_adm_doc', 'uuid',
                             'date_added', 'date_updated')
    form_rules = (
        FieldSet(('full_name', 'short_name', 'inn', 'ogrn'),
                 'Основные реквизиты организации'),
        FieldSet(('factual_address', 'region'),
                 'Адресная информация'),
        FieldSet(('boss_position', 'boss_fio', 'contacts'),
                 'Контактные данные'),
        FieldSet(('date_agreement', 'agreement_unit'),
                 'Соглашение о сотрудничестве'),
        FieldSet(('is_gov', 'is_military'),
                 'Характеристики организации'))
    form_widget_args = dictionary.organization_fields_placeholders

    @expose('/')
    def index_view(self):
        """Расширяет view-класс для возможности обновления
         динамических фильтров."""
        self.dynamic_filters = []
        self.dynamic_filters.extend(
            [
                OrgRegionFilter(
                    None,
                    name='Регион(-ы)',
                    options=get_instance_choices(Region,
                                                 'region_id',
                                                 'name')
                ),
                OrgDocumentsFilter(
                    None,
                    name='Наличие документа(-ов)',
                    options=get_instance_choices(
                        OrgAdmDoc,
                        'orgadm_id',
                        'name',
                        _name_limiter=ORGADM_DOC_NAME_CONST
                    )
                )
            ]
        )
        self._refresh_filters_cache()
        return super(OrganizationModelView, self).index_view()

    @expose('/<int:org_id>/documents/', methods=['GET', 'POST'])
    def org_documents_view(self, org_id: int):
        """View-функция для вложения документов организаций."""
        org = Organization.query.get_or_404(org_id)
        form = AddSubjectDocumentForm()
        form.submit.label.text = "Добавить"
        form.organization_name.data = org.short_name
        orgadmdoc_options = OrgAdmDoc.query.order_by(OrgAdmDoc.name).all()
        form.org_documents.choices = [
            (doc.orgadm_id, doc.name) for doc in orgadmdoc_options
        ]

        if form.validate_on_submit():
            document = OrgAdmDoc.query.get_or_404(form.org_documents.data)
            date_approved = form.date_approved.data
            our_inbox_number = form.our_inbox_number.data
            props = form.props.data or None

            org_adm_doc_exists = (
                (OrgAdmDocOrganization
                 .query
                 .filter(OrgAdmDocOrganization.organization == org)
                 .filter(OrgAdmDocOrganization.org_doc == document))
            ).first()

            if org_adm_doc_exists:
                old_org_doc = org_adm_doc_exists
                old_org_doc.date_approved = date_approved
                old_org_doc.our_inbox_number = our_inbox_number
                old_org_doc.props = props
                db.session.add(old_org_doc)
            else:
                new_org_doc = OrgAdmDocOrganization(
                    organization=org,
                    org_doc=document,
                    date_approved=date_approved,
                    our_inbox_number=our_inbox_number,
                    props=props
                )
                db.session.add(new_org_doc)
            uploaded_file = form.doc_file.data
            dir_name = os.path.join(current_app.config['DIR_WITH_ORG_FILES'],
                                    org.first_two_uuid_symb,
                                    org.uuid)
            try:
                os.makedirs(dir_name, exist_ok=True)
            except Exception:
                raise DirNotCreatedError(DIR_NOT_CREATED_MSG)
            filename = os.path.join(dir_name,
                                    create_dot_pdf(document.name_prefix)
                                    )
            if uploaded_file:
                if uploaded_file.mimetype != PDF_MIMETYPE_CONST:
                    return abort(HTTPStatus.BAD_REQUEST,
                                 NOT_PDF_MIMETYPE_MSG)
                try:
                    uploaded_file.save(filename)
                except Exception:
                    raise OrgFileNotSavedError(FILE_NOT_CREATED_MSG)
            else:
                try:
                    create_pdf(filename)
                except Exception:
                    raise OrgPDFNotCreatedError(BASE_PDF_NOT_CREATED_MSG)
            db.session.commit()
            flash(SUCCESS_DATA_UPLOAD_MSG)
            return redirect(url_for("organizations.details_view",
                                    id=org.org_id)
                            )
        return self.render('admin/org_add_document.html', form=form)

    @expose('/<int:org_id>/documents/<int:doc_id>/', methods=['GET'])
    def return_org_document(self, org_id: int, doc_id: int):
        """Возвращает файл документа организации."""
        org = db.session.query(Organization).get_or_404(org_id)
        doc = OrgAdmDoc.query.get_or_404(doc_id)
        file_path = os.path.join(current_app.config['DIR_WITH_ORG_FILES'],
                                 org.first_two_uuid_symb,
                                 org.uuid,
                                 create_dot_pdf(doc.name_prefix))
        attach_file_name = (f'{date.today()}'
                            f'-{org.short_name[:FILENAME_CONST]}'
                            f'-{doc.name[:FILENAME_CONST]}')
        attach_file_name = create_dot_pdf(attach_file_name)
        return send_file(file_path, as_attachment=True,
                         attachment_filename=attach_file_name)
