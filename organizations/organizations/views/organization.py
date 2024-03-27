import os
import shutil
import zipfile
from datetime import date

import pycdlib
from babel.dates import format_date
from docxtpl import DocxTemplate
from flask import current_app as app
from flask import flash, redirect, request, send_file, url_for
from flask_admin import expose
from flask_admin.form.rules import FieldSet
from wtforms.validators import Optional

from ..extentions import db
from ..filters import (OrgDocumentsAndFilter, OrgHasAgreementFilter,
                       OrgOkrugFilter, OrgOkrugNotFilter, OrgRegionFilter,
                       OrgRegionNotFilter)
from ..forms import (AddSubjectDocumentForm, SendMethodDocsToOrgForm,
                     sender_choices, validate_email, validate_future_date,
                     validate_inn, validate_kpp, validate_ogrn)
from ..lingva_master import LingvaMaster
from ..models import (Contact, Message, MethodicalDoc, Okrug, OrgAdmDoc,
                      OrgAdmDocOrganization, Organization, Region)
from ..utils import (cast_string_to_non_breaking_space, create_dot_pdf,
                     create_pdf, get_alpha_num_string, get_instance_choices)
from ..views import forms_placeholders as dictionary
from .markup_formatters import org_name_formatter
from .master import BaseModelView
from .system_messages_for_user import (ADM_DOC_CONF_FILE_NOT_CREATED_TEXT,
                                       ADM_DOC_DIR_NOT_CREATED_TEXT,
                                       ADM_DOC_FILE_IS_NOT_PDF_TEXT,
                                       ADM_DOC_FILE_NOT_CREATED_TEXT,
                                       FLASH_ERROR,
                                       METHOD_DOC_ARCHIVE_NOT_CREATED_TEXT,
                                       METHOD_DOC_DIR_NOT_CREATED_TEXT,
                                       METHOD_DOC_ISO_NOT_CREATED_TEXT,
                                       METHOD_DOC_LETTER_NOT_CREATED_TEXT,
                                       SUCCESS_DATA_UPLOAD_MSG)

# Служебные константы
FILENAME_CONST = 20
ORGADM_DOC_NAME_CONST = 80
PDF_MIMETYPE_CONST = "application/pdf"
LETTER_PHRASE_WITH_NON_BREAKABLE_SPACE = 'Российской Федерации'

# Константы для моделей
SEARCH_MODEL_TEXT = "Название, ИНН, КПП"

# Настраиваемые константы для осуществления действий
LETTER_DATE_FORMAT = "%d.%m.%Y"
METHOD_DOC_ARCHIVE_NAME = "методические документы.zip"
METHOD_DOC_CONF_TEXT = 'Конфиденциально'
METHOD_DOC_DOCX_FILE_NAME = '.docx'
METHOD_DOC_INPUT_MESSAGE_REQUEST_TEXT = 'Запрос методических документов'
METHOD_DOC_ISO_FILE_NAME = '.iso'
METHOD_DOC_OUTPUT_MESSAGE_TEXT = 'О направлении методических документов'
METHOD_DOC_OUTPUT_NUMBER_TEXT = 'номер и дату необходимо заполнить'


class OrganizationModelView(BaseModelView):
    """View-класс организации."""

    def on_model_change(self, form, model, is_created) -> None:
        """Переопределяет поведение создания и изменения организации.
        Создает строку, используемую для поиска из полного наименования
         организации. Заменяет значения '' у полей типа db.Text на None."""
        if model.full_name:
            model.full_name = model.full_name.upper()
            model.short_name = model.short_name.upper()
            model.db_name = get_alpha_num_string(model.full_name)

        model.contacts = form.contacts.data or None
        model.factual_address = form.factual_address.data or None
        model.mailing_address = form.mailing_address.data or None
        model.agreement_unit = form.agreement_unit.data or None

    def get_details_grouped(self) -> dict:
        """Создает сгруппированный словарь данных для
         удобного отображения сведений об организации."""
        return dictionary.get_beautiful_org_formatter(self)

    # MAIN options
    column_export_exclude_list = ['uuid', 'org_id', 'db_name',
                                  'date_added', 'boss_fio',
                                  'boss_position', 'main_unit',
                                  'date_updated', 'is_active']
    # LIST options
    list_template = 'admin/org_list.html'

    column_default_sort = [('date_updated', True),
                           ('date_added', True),
                           ('full_name', False),
                           ('inn', False)]

    column_descriptions = dictionary.organization_fields_descriptions
    column_editable_list = ['contacts']
    column_exclude_list = ['short_name', 'uuid', 'id', 'date_added',
                           'date_updated', 'region_id', 'ogrn', 'db_name',
                           'agreement_unit', 'boss_fio', 'is_gov',
                           'boss_position', 'factual_address',
                           'mailing_address',
                           'is_military', 'is_active']
    column_filters = ('db_name',
                      OrgHasAgreementFilter(
                          Organization.date_agreement,
                          'Наличие соглашения о сот-ве'
                      ),
                      'is_gov'
                      )

    column_formatters = {
        "full_name": org_name_formatter
    }

    column_formatters_export = dict()

    column_labels = dictionary.organization_fields_labels
    column_searchable_list = ['db_name', 'short_name', 'inn', 'kpp']

    def search_placeholder(self):
        """Переопределяет текст, отображаемый в Поиске
         по модели организации."""
        return SEARCH_MODEL_TEXT

    column_sortable_list = ('full_name', ('region', 'region.name'),
                            'date_agreement')

    # RETRIEVE OPTIONS
    details_template = 'admin/org_details.html'
    details_columns_grouped = get_details_grouped
    details_grouped = True

    # CREATE / UPDATE options
    form_args = {
        "date_agreement": {
            "validators": [validate_future_date],
            "description": None},
        "inn": {"validators": [Optional(), validate_inn],
                "description": None},
        "ogrn": {"validators": [Optional(), validate_ogrn],
                 "description": None},
        "kpp": {"validators": [Optional(), validate_kpp],
                "description": None},
        "full_name": {"description": None},
        "short_name": {"description": None},
        "factual_address": {"description": None},
        "mailing_address": {"description": None},
        "region": {"description": None},
        "boss_position": {"description": None},
        "boss_fio": {"description": None},
        "contacts": {"description": None},
        "agreement_unit": {"description": None},
        "com_contacts": {"description": None}

    }

    form_rules = (
        FieldSet(('full_name', 'short_name', 'inn', 'kpp', 'ogrn'),
                 'Основные реквизиты'),
        FieldSet(('factual_address', 'mailing_address', 'region'),
                 'Адресная информация'),
        FieldSet(('boss_position', 'boss_fio', 'contacts'),
                 'Контактные данные'),
        FieldSet(('date_agreement', 'agreement_unit'),
                 'Соглашение о сотрудничестве'),
        FieldSet(('is_gov', 'is_military'),
                 'Характеристики'),
        FieldSet(('com_contacts',), 'Контактные данные NEW')
    )

    inline_models = [
        (Contact,
         dict(form_columns=['contact_id', 'fio',
                            'dep', 'pos', 'mob_phone',
                            'work_phone', 'email', 'is_main'],
              column_labels=dictionary.contact_fields_labels,
              form_args={
                  "email": {"validators": [Optional(), validate_email]},
                  "work_phone": {"validators": []},
                  "mob_phone": {"validators": []}},
              form_widget_args=dictionary.contact_fields_placeholders)
         )
    ]

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
                    name='Регион(-ы) организаций',
                    options=get_instance_choices(Region,
                                                 'region_id',
                                                 'name')
                ),
                OrgRegionNotFilter(
                    None,
                    name='Регион(-ы) организаций',
                    options=get_instance_choices(Region,
                                                 'region_id',
                                                 'name')
                ),
                OrgOkrugFilter(
                    None,
                    name='Округ(-и) организаций',
                    options=get_instance_choices(Okrug,
                                                 'okrug_id',
                                                 'name')
                ),
                OrgOkrugNotFilter(
                    None,
                    name='Округ(-и) организаций',
                    options=get_instance_choices(Okrug,
                                                 'okrug_id',
                                                 'name')
                ),
                OrgDocumentsAndFilter(
                    None,
                    name='Наличие документа(-ов)',
                    options=get_instance_choices(
                        OrgAdmDoc,
                        'orgadm_id',
                        'name',
                        _name_limiter=ORGADM_DOC_NAME_CONST
                    )
                ),
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

            # document
            date_approved = form.date_approved.data
            props = form.props.data or None
            comment = form.comment.data or None

            # message
            our_inbox_number = form.our_inbox_number.data
            date_registered = form.date_registered.data
            number_inbox_approved = form.number_inbox_approved.data
            date_inbox_approved = form.date_inbox_approved.data

            if (
                    date_registered
                    or date_inbox_approved
                    or len(our_inbox_number) > 0
                    or len(number_inbox_approved) > 0):
                information = f'о направлении документа "{document.name}"'

                message = Message(our_inbox_number=our_inbox_number,
                                  date_registered=date_registered,
                                  number_inbox_approved=number_inbox_approved,
                                  date_inbox_approved=date_inbox_approved,
                                  information=information)

                org.messages.append(message)
                db.session.add(org)

            org_adm_doc_exists = (
                (OrgAdmDocOrganization
                 .query
                 .filter(OrgAdmDocOrganization.organization == org)
                 .filter(OrgAdmDocOrganization.org_doc == document)
                 )
            ).first()

            if org_adm_doc_exists:
                old_org_doc = org_adm_doc_exists
                old_org_doc.date_approved = date_approved
                old_org_doc.props = props
                old_org_doc.comment = comment

                db.session.add(old_org_doc)
            else:
                new_org_doc = OrgAdmDocOrganization(
                    organization=org,
                    org_doc=document,
                    date_approved=date_approved,
                    props=props,
                    comment=comment
                )
                db.session.add(new_org_doc)

            if document.is_main:
                org.date_agreement = date_approved
                db.session.add(org)

            uploaded_file = form.doc_file.data
            dir_name = os.path.join(
                app.config['BUSINESS_LOGIC']['ORG_FILES_DIR'],
                org.first_two_uuid_symb,
                org.uuid)
            try:
                os.makedirs(dir_name, exist_ok=True)
            except OSError as e:
                flash(ADM_DOC_DIR_NOT_CREATED_TEXT,
                      category=FLASH_ERROR)
                app.logger.error(e)
                return redirect(url_for(
                    "organizations.org_documents_view",
                    org_id=org.org_id)
                )

            filename = os.path.join(dir_name,
                                    create_dot_pdf(document.name_prefix)
                                    )
            if uploaded_file:
                if uploaded_file.mimetype != PDF_MIMETYPE_CONST:
                    flash(ADM_DOC_FILE_IS_NOT_PDF_TEXT,
                          category=FLASH_ERROR)
                    return redirect(url_for(
                        "organizations.org_documents_view",
                        org_id=org.org_id)
                    )
                try:
                    uploaded_file.save(filename)
                except OSError as e:
                    flash(ADM_DOC_FILE_NOT_CREATED_TEXT,
                          category=FLASH_ERROR)
                    app.logger.error(e)
                    return redirect(url_for(
                        "organizations.org_documents_view",
                        org_id=org.org_id)
                    )
            else:
                try:
                    create_pdf(filename)
                except Exception as e:
                    flash(ADM_DOC_CONF_FILE_NOT_CREATED_TEXT,
                          category=FLASH_ERROR)
                    app.logger.error(e)
                    return redirect(url_for(
                        "organizations.org_documents_view",
                        org_id=org.org_id)
                    )

            db.session.commit()
            flash(SUCCESS_DATA_UPLOAD_MSG,
                  category='success')
            return redirect(url_for("organizations.details_view",
                                    id=org.org_id)
                            )
        return self.render('admin/org_add_document.html', form=form)

    @expose('/<int:org_id>/documents/<int:doc_id>/', methods=['GET'])
    def return_org_document(self, org_id: int, doc_id: int):
        """Возвращает файл документа организации."""
        org = db.session.query(Organization).get_or_404(org_id)
        doc = OrgAdmDoc.query.get_or_404(doc_id)
        file_path = os.path.abspath(
            os.path.join(
                app.config['BUSINESS_LOGIC']['ORG_FILES_DIR'],
                org.first_two_uuid_symb,
                org.uuid,
                create_dot_pdf(doc.name_prefix)
            )
        )
        attach_file_name = (f'{date.today()}'
                            f'-{org.short_name[:FILENAME_CONST]}'
                            f'-{doc.name[:FILENAME_CONST]}')
        attach_file_name = create_dot_pdf(attach_file_name)
        return send_file(file_path, as_attachment=True,
                         attachment_filename=attach_file_name)

    @expose('<int:org_id>/resources/', methods=['GET', 'POST'])
    def org_resources_view(self, org_id: int):
        """Возвращает действующие информационные ресурсы организаций."""
        org = Organization.query.get_or_404(org_id)
        s_resources = [(res.resource_id, res.name) for res in org.resources]
        return dict(s_resources)

    @expose('<int:org_id>/send-method-docs/', methods=['GET', 'POST'])
    def org_send_method_docs(self, org_id: int):
        """View-функция для отправки организации методических документов."""
        org = Organization.query.get_or_404(org_id)
        form = SendMethodDocsToOrgForm()

        method_docs = (db.session
                       .query(MethodicalDoc)
                       .filter(MethodicalDoc.is_active.is_(True))
                       .order_by(MethodicalDoc.name)
                       .all()
                       )

        form.method_docs.choices = [
            (method_doc.method_id,
             method_doc.name)
            for method_doc in method_docs
        ]

        form.submit.label.text = "Создать письмо"
        form.organization_name.data = org.short_name

        if form.validate_on_submit() and request.method == 'POST':
            recipient_position = form.recipient_position.data
            recipient_fio = form.recipient_fio.data
            recipient_gender = form.recipient_gender.data
            recipient_address = form.org_address.data

            our_inbox_number = form.our_inbox_number.data
            date_registered = form.date_registered.data
            number_inbox_approved = form.number_inbox_approved.data
            date_inbox_approved = form.date_inbox_approved.data

            chosen_method_docs = form.method_docs.data
            disk = form.disk.data

            sender_position = form.sender.data

            chosen_method_docs = (
                db.session
                .query(MethodicalDoc)
                .filter(MethodicalDoc.method_id.in_(chosen_method_docs))
                .order_by(MethodicalDoc.name)
                .all()
            )

            rel_dir_for_results = (f'{str(date.today())}'
                                   f'-{org.get_org_dir_name()}')

            abs_dir_for_results = os.path.join(
                app.config['BUSINESS_LOGIC']['METHOD_DOCS_PATH'],
                rel_dir_for_results)

            old_mask = os.umask(0o022)
            try:
                os.umask(0o000)
                os.makedirs(abs_dir_for_results, mode=0o777, exist_ok=True)
            except OSError as e:
                flash(METHOD_DOC_DIR_NOT_CREATED_TEXT,
                      category=FLASH_ERROR)
                app.logger.error(e)
                return redirect(url_for(
                    "organizations.org_send_method_docs",
                    org_id=org.org_id)
                )

            zip_path = os.path.join(abs_dir_for_results,
                                    METHOD_DOC_ARCHIVE_NAME)

            try:
                with zipfile.ZipFile(zip_path, 'w') as zf:
                    for chosen_method_doc in chosen_method_docs:
                        data = zipfile.ZipInfo(chosen_method_doc.get_file_name)
                        data.compress_type = zipfile.ZIP_DEFLATED
                        zf.writestr(data, chosen_method_doc.get_file.read())
                application_file_name = os.path.basename(zip_path)
            except Exception as e:
                flash(METHOD_DOC_ARCHIVE_NOT_CREATED_TEXT,
                      category=FLASH_ERROR)
                app.logger.error(e)
                shutil.rmtree(abs_dir_for_results)
                return redirect(url_for(
                    "organizations.org_send_method_docs",
                    org_id=org.org_id)
                )
            else:
                iso = pycdlib.PyCdlib()
                iso.new(joliet=3)
                iso.add_file(zip_path,
                             joliet_path=os.path.join('/',
                                                      application_file_name
                                                      )
                             )
                iso_path = os.path.join(
                    abs_dir_for_results,
                    rel_dir_for_results + METHOD_DOC_ISO_FILE_NAME
                )
                try:
                    iso.write(iso_path)
                except Exception as e:
                    flash(METHOD_DOC_ISO_NOT_CREATED_TEXT,
                          category=FLASH_ERROR)
                    app.logger.error(e)
                    return redirect(url_for(
                        "organizations.org_send_method_docs",
                        org_id=org.org_id)
                    )
                finally:
                    iso.close()

            inbox_message = None
            letter_previous_link = None
            letter_conf_text = None
            if (
                    date_registered
                    or date_inbox_approved
                    or len(our_inbox_number) > 0
                    or len(number_inbox_approved) > 0):

                inbox_message = Message(
                    our_inbox_number=our_inbox_number,
                    date_registered=date_registered,
                    number_inbox_approved=number_inbox_approved,
                    date_inbox_approved=date_inbox_approved,
                    information=METHOD_DOC_INPUT_MESSAGE_REQUEST_TEXT
                )

                org.messages.append(inbox_message)

                if date_inbox_approved and len(number_inbox_approved) > 0:
                    letter_previous_link = (
                        f'(на № {number_inbox_approved} от '
                        f'{date_inbox_approved.strftime(LETTER_DATE_FORMAT)})'
                    )

            outbox_message = Message(
                parent=inbox_message,
                information=METHOD_DOC_OUTPUT_MESSAGE_TEXT,
                our_outbox_number=METHOD_DOC_OUTPUT_NUMBER_TEXT,
                date_approved=date.today(),
                is_inbox=False
            )

            org.messages.append(outbox_message)
            outbox_message.methodical_docs.extend(chosen_method_docs)
            db.session.add(org)

            recipient = LingvaMaster(gender=recipient_gender,
                                     fio=recipient_fio)

            org.boss_fio = recipient.fio
            org.boss_position = recipient_position
            org.mailing_address = recipient_address
            docx = DocxTemplate(
                app.config['BUSINESS_LOGIC']['METHOD_DOC_TEMPLATE'])

            if [doc.is_conf for doc in chosen_method_docs if doc.is_conf]:
                letter_conf_text = METHOD_DOC_CONF_TEXT

            letter_application = (f'файл "{application_file_name}",'
                                  f' {os.path.getsize(zip_path)} байт')
            letter_header = METHOD_DOC_OUTPUT_MESSAGE_TEXT
            letter_greeting = recipient.get_doc_greeting()

            letter_month_year = (format_date(
                date.today(),
                locale='ru',
                format='MMMM YYYY') + ' г.')

            method_docs_names = []
            for doc in chosen_method_docs:
                doc_name = doc.name_for_letter or doc.name
                if LETTER_PHRASE_WITH_NON_BREAKABLE_SPACE in doc_name:
                    doc_name = cast_string_to_non_breaking_space(
                        doc_name,
                        LETTER_PHRASE_WITH_NON_BREAKABLE_SPACE
                    )
                method_docs_names.append(f'"{doc_name}"')
            letter_method_docs = "; ".join(method_docs_names)

            letter_context = {
                'recipient_position': recipient_position,
                'recipient_initials':
                    recipient.get_dative_last_name_with_initials(),
                'recipient_address': recipient_address,
                'letter_month_year': letter_month_year,
                'letter_header': letter_header,
                'letter_previous_link': letter_previous_link,
                'letter_greeting': letter_greeting,
                'letter_method_docs': letter_method_docs,
                'disk': disk,
                'letter_application': letter_application,
                'letter_conf_text': letter_conf_text,
                'letter_sender_position': sender_position,
                'letter_sender_fio': sender_choices[sender_position]
            }

            try:
                docx.render(letter_context)
            except Exception as e:
                flash(METHOD_DOC_LETTER_NOT_CREATED_TEXT,
                      category=FLASH_ERROR)
                app.logger.error(e)
                db.session.rollback()
                shutil.rmtree(abs_dir_for_results)
                return redirect(url_for(
                    "organizations.org_send_method_docs",
                    org_id=org.org_id)
                )
            else:
                docx_path = os.path.join(
                    abs_dir_for_results,
                    rel_dir_for_results + METHOD_DOC_DOCX_FILE_NAME
                )
                docx.save(docx_path)
                os.umask(old_mask)
                os.remove(zip_path)
                db.session.commit()
                flash(SUCCESS_DATA_UPLOAD_MSG,
                      category='success')
                return redirect(url_for(
                    "organizations.details_view",
                    id=org.org_id)
                )

        form.org_address.data = org.mailing_address or org.factual_address
        form.recipient_fio.data = org.boss_fio
        form.recipient_position.data = org.boss_position
        return self.render('admin/org_send_method_docs.html', form=form)
