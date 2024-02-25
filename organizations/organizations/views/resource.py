import re

from flask import flash
from flask_admin import expose
from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader
from sqlalchemy import func

from ..extentions import db
from ..filters import (ResourceIndustryFilter, ResourceOkrugFilter,
                       ResourceRegionFilter)
from ..models import Address, Industry, Okrug, Organization, Region
from ..utils import get_instance_choices
from ..views import forms_placeholders as dictionary
from .markup_formatters import org_list_formatter
from .master import BaseModelView
from .system_messages_for_user import FLASH_ERROR

CHOOSE_SINGLE_ORG_TEXT = "Выберете организацию"
INDEX_PATTERN = r"((?<!\d)\d{6}(?!\d))"
RESOURCE_AJAX_OWNER_CONST = 3
RESOURCE_NOT_DELETED_MSG = "Ресурсы не были удалены!"


class ResourceModelView(BaseModelView):
    """View-класс информационного ресурса."""

    def is_visible(self):
        return False

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
    can_delete = False
    can_create = False
    can_edit = False

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
    column_searchable_list = ['name']

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
            fields=['db_name', 'short_name'],
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
