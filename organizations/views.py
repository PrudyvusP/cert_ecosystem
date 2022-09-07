import os
import re
from datetime import date
from http import HTTPStatus
from typing import List, Tuple

from config import Config
from flask import Markup
from flask import flash, url_for, redirect, abort, send_file
from flask_admin import AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader
from flask_admin.form.rules import FieldSet
from flask_admin.model import typefmt
from sqlalchemy import func
from wtforms.validators import Length, InputRequired, Optional

import organizations.forms_placeholders as dictionary
from .exceptions import (OrgFileNotSavedError, DirNotCreatedError,
                         OrgPDFNotCreatedError, ModelAttributeError)
from .extentions import db
from .filters import (OrgRegionFilter,
                      OrgHasAgreementFilter, OrgIsSubjectKIIFilter,
                      OrgHasHadAnyContactsWithUsFilter, OrgDocumentsFilter,
                      ResourceRegionFilter, ResourceIndustryFilter,
                      ResourceOkrugFilter)
from .forms import (AddSubjectDocumentForm, validate_future_date,
                    validate_inn, validate_ogrn)
from .models import (Organization, Region, OrgAdmDoc,
                     OrgAdmDocOrganization, Message, Address, Industry, Okrug)
from .utils import (create_pdf, create_prefix, create_dot_pdf,
                    get_alpha_num_string, create_a_href_string)


CHOOSE_MAIN_MESSAGE_TEXT = "Выберете письмо-основание"
CHOOSE_MULT_ORG_TEXT = "Выберете организацию (-и)"
CHOOSE_SINGLE_ORG_TEXT = "Выберете организацию"
DEFAULT_PAGE_SIZE_CONST = 20
DIR_NOT_CREATED_MSG = "Главная директория организаций не создалась"
BASE_PDF_NOT_CREATED_MSG = "Базовый pdf-файл не смог создаться"
FILE_NOT_CREATED_MSG = "Образ документа не смог сохраниться"
FILENAME_CONST = 20
FLASH_ERROR = "error"
INDEX_PATTERN = r"((?<!\d)\d{6}(?!\d))"
MESSAGE_DATE_REGISTERED_TEXT = ("Дата подписи не может"
                                " быть позже даты регистрации!")
MESSAGE_INFORMATION_MIN_CONST = 10
MESSAGE_NO_ORG_CHOSEN_TEXT = "Не выбрана организация"
MESSAGE_TYPE_TEXT = "Письмо либо исходящее, либо входящее!"
MESSAGE_VISIBLE_LEN_CONST = 70
NOT_PDF_MIMETYPE_MSG = "Not PDF!"
ORGADM_DOC_NAME_CONST = 80
PDF_MIMETYPE_CONST = "application/pdf"
RESOURCE_AJAX_OWNER_CONST = 3
RESOURCE_NOT_DELETED_MSG = "Ресурсы не были удалены!"
SUCCESS_DATA_UPLOAD_MSG = "Данные успешно добавлены"
SYMB_CONST = "—"

dir_with_org_files = os.path.join(Config.BASE_DIR,
                                  "organizations",
                                  Config.STATIC_FOLDER,
                                  "organizations")

DATE_DEFAULT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
DATE_DEFAULT_FORMATTERS.update({
    date: lambda f, x: x.strftime("%d-%m-%Y"),
})

MESSAGE_DEFAULT_FORMATTERS = DATE_DEFAULT_FORMATTERS.copy()
MESSAGE_DEFAULT_FORMATTERS.update({
    type(None): lambda view, value: SYMB_CONST if value is None else "",
})


def get_instance_choices(model,
                         _id: str = "id",
                         _name: str = "name",
                         _name_limiter: int = None,
                         ) -> List[Tuple[int, str]]:
    """Возвращает опции для html-элемента SelectField
    переданной в функцию модели."""
    try:
        _id = getattr(model, _id)
        _name = getattr(model, _name)
    except AttributeError:
        raise ModelAttributeError
    q = model.query.with_entities(_id, _name).order_by(_name).all()
    if not _name_limiter:
        return q
    return [(param[0], param[1][:_name_limiter]) for param in q]


def org_list_formatter(view, context, model, name) -> str:
    """Возвращает удобное отображение организаций в таблице."""
    org_data = getattr(model, name)
    if org_data:
        results = []
        if isinstance(org_data, Organization):
            org_full_name = getattr(org_data, "full_name")
            url = url_for("organizations.details_view", id=org_data.org_id)
            return Markup(create_a_href_string(url, org_full_name))
        else:
            for org in org_data:
                url = url_for("organizations.details_view", id=org.org_id)
                full_url = create_a_href_string(url, org.full_name)
                results.append(full_url)
            markup_string = "<br><br>".join(results)
            return Markup(markup_string)
    return SYMB_CONST


def parent_single_formatter(view, context, model, name) -> str:
    """Возвращает удобное отображение письма-родителя в таблице."""
    if model.parent:
        url = url_for('message.details_view', id=model.parent.message_id)
        full_url = f"<a href={url}>{str(model.parent)}</a>"
        return Markup(full_url)
    return SYMB_CONST


def children_list_formatter(view, context, model, name):
    """Возвращает удобное отображение писем-потомков в таблице."""
    if model.children:
        results = []
        for child in model.children:
            url = url_for('message.details_view', id=child.message_id)
            full_url = f"<a href={url}>{str(child)}</a>"
            results.append(full_url)
        markup_string = ', '.join(results)
        return Markup(markup_string)
    return SYMB_CONST


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


class HomeView(AdminIndexView):
    """View для главной страницы админки
    Создана, чтобы скрыть кнопку в меню."""

    def is_visible(self):
        return False


class WorkspaceView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        return "rofel-fm"
        #return self.render('analytics_index.html')


class OrgAdmDocModelView(ModelView):
    """View-класс организационно-распорядительного
     документа организации."""
    can_create = True
    can_view_details = False
    can_edit = True
    can_delete = False

    column_list = ['name']
    column_labels = dictionary.orgadmdoc_fields_labels

    form_excluded_columns = ('name_prefix', 'organization',
                             'date_added', 'date_updated')

    def on_model_change(self, form, model, is_created):
        """Переопределяет создание/изменение модели документа.
         Создает префикс документа по его названию."""
        if is_created:
            model.name_prefix = create_prefix(model.name)


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

    column_searchable_list = ['information']
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
            dir_name = os.path.join(dir_with_org_files,
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
        file_path = os.path.join(dir_with_org_files,
                                 org.first_two_uuid_symb,
                                 org.uuid,
                                 create_dot_pdf(doc.name_prefix))
        attach_file_name = (f'{date.today()}'
                            f'-{org.short_name[:FILENAME_CONST]}'
                            f'-{doc.name[:FILENAME_CONST]}')
        attach_file_name = create_dot_pdf(attach_file_name)
        return send_file(file_path, as_attachment=True,
                         attachment_filename=attach_file_name)


class ResourceModelView(CreateRetrieveUpdateModelView):
    """View-класс информационного ресурса."""

    def get_query(self):
        """Переопределяет SELECT-запрос по умолчанию к БД
        с целью исключить из выборки неактивные информационные ресурсы."""
        return (super(ResourceModelView, self)
                .get_query()
                .filter(self.model.is_active.is_(True))
                )

    def get_count_query(self):
        """Переопределяет COUNT(SELECT-запрос по умолчанию к БД)
        с целью исключить из подсчета количества ресурсов неактивные."""
        return (self.session
                .query(func.count('*'))
                .filter(self.model.is_active.is_(True))
                )

    def on_model_change(self, form, model, is_created):
        """Переопределяет поведение создания и изменения ресурса.
         Определяет регионы в адресной строке по наличию
         почтовых индексов в ней."""
        raw_address = model.factual_addresses
        # TODO вместо None сохраняется пустая строка
        if raw_address:
            raw_address = raw_address.lower()
            indexes = map(int,
                          re.findall(INDEX_PATTERN, raw_address)
                          )
            regions = set()
            for index in indexes:
                address = db.session.query(Address).get(index)
                if address:
                    regions.add(address.region)
            if regions:
                model.regions.extend(list(regions))
                db.session.commit()

    def delete_model(self, model):
        """Переопределяет поведение при удалении информационного
        ресурса (флажок is_active=False вместо физического удаления)."""
        try:
            self.on_model_delete(model)
            self.session.flush()
            if hasattr(model, 'is_active'):
                model.is_active = False
            self.session.commit()
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(RESOURCE_NOT_DELETED_MSG,
                      category=FLASH_ERROR)
            self.session.rollback()
            return False
        else:
            self.after_model_delete(model)
        return True

    def get_details_grouped(self) -> dict:
        """Создает сгруппированный словарь данных для
         удобного отображения сведений об организации."""
        return dictionary.get_beautiful_res_formatter(self)

    # MAIN options
    can_delete = True
    column_export_exclude_list = ['uuid', 'org_id', 'executor',
                                  'addition_info', 'org_id']

    # LIST OPTIONS
    column_descriptions = dictionary.resource_fields_description
    column_formatters = {
        "org_owner": org_list_formatter
    }
    column_filters = ['category', 'org_owner.db_name',
                      'name', 'is_okii', 'fstec_reg_number']
    column_labels = dictionary.resource_fields_labels
    column_labels['org_owner.db_name'] = 'Название владельца'
    column_list = ['name', 'is_okii', 'fstec_reg_number', 'category',
                   'org_owner']
    column_sortable_list = ['name', 'is_okii', 'fstec_reg_number',
                            ('org_owner', 'org_owner.short_name')]
    column_searchable_list = ['fstec_reg_number']

    # RETRIEVE OPTIONS
    details_template = 'admin/res_details.html'
    details_columns_grouped = get_details_grouped
    details_grouped = True
    column_details_list = ['is_okii', 'fstec_reg_number',
                           'name', 'category', 'date_added_to_fstec',
                           'date_updated_to_fstec', 'factual_addresses',
                           'resp_worker', 'ip_pool', 'dns_pool', 'regions',
                           'industries', 'org_owner']

    # CREATE / UPDATE options
    form_ajax_refs = {
        'org_owner': QueryAjaxModelLoader(
            'org_owner',
            db.session,
            Organization,
            fields=['db_name'],
            filters=['is_active=True'],
            order_by='full_name',
            placeholder=CHOOSE_SINGLE_ORG_TEXT,
            minimum_input_length=RESOURCE_AJAX_OWNER_CONST)
    }
    form_excluded_columns = ['regions', 'industries', 'uuid',
                             'date_added', 'date_updated', 'is_okii',
                             'fstec_reg_number', 'category',
                             'date_added_to_fstec', 'is_active',
                             'date_updated_to_fstec', 'outsource_org']
    form_widget_args = dictionary.resource_fields_placeholders

    @expose('/')
    def index_view(self):
        """Расширяет view-класс для возможности обновления
         динамических фильтров."""
        self.dynamic_filters = []
        self.dynamic_filters.extend(
            [
                ResourceOkrugFilter(
                    None,
                    name='Округа',
                    options=get_instance_choices(Okrug,
                                                 'okrug_id',
                                                 'name')
                ),
                ResourceRegionFilter(
                    None,
                    name='Регион(-ы)',
                    options=get_instance_choices(Region,
                                                 'region_id',
                                                 'name')
                ),
                ResourceIndustryFilter(
                    None,
                    name='Сферы',
                    options=get_instance_choices(Industry,
                                                 'industry_id',
                                                 'name')
                ),

            ]
        )
        self._refresh_filters_cache()
        return super(ResourceModelView, self).index_view()
