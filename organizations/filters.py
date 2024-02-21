from flask_admin.babel import lazy_gettext
from flask_admin.contrib.sqla import filters
from sqlalchemy import func

from .extentions import db
from .models import (Organization, Resource, Responsibility,
                     Region, OrgAdmDocOrganization, Industry,
                     MethodicalDoc, Message)

OPTIONS = [('да', 'Да'), ('нет', 'Нет')]


class OrgHasAgreementFilter(filters.BaseSQLAFilter):
    """Фильтр на список организаций,
    с которыми есть соглашение."""

    def apply(self, query, value, alias=None):
        if value == "да":
            return query.filter(self.get_column(alias).isnot(None))
        return query.filter(self.get_column(alias).is_(None))

    def operation(self):
        return lazy_gettext('есть')

    def get_options(self, view):
        return OPTIONS


class OrgRegionFilter(filters.FilterInList):
    """Фильтр на список организаций,
    расположенных в регионах, id которых переданы."""

    def apply(self, query, value, alias=None):
        return query.filter(Organization.region_id.in_(value))


class OrgRegionNotFilter(filters.FilterNotInList):
    """Фильтр на список организаций,
    расположенных не в регионах, id которых переданы."""

    def apply(self, query, value, alias=None):
        return query.filter(~Organization.region_id.in_(value))

    def operation(self):
        return lazy_gettext('не в списке')


class OrgOkrugFilter(filters.FilterInList):
    """Фильтр на список организаций,
    расположенных в округах, id которых переданы."""

    def apply(self, query, value, alias=None):
        org_ids = (
            db.session
            .query(Organization.org_id.distinct())
            .join(Region, Organization.region_id == Region.region_id)
            .filter(Region.okrug_id.in_(value))
        )

        return query.filter(Organization.org_id.in_(org_ids))


class OrgOkrugNotFilter(filters.FilterNotInList):
    """Фильтр на список организаций,
    расположенных не в округах, id которых переданы."""

    def apply(self, query, value, alias=None):
        org_ids = (
            db.session
            .query(Organization.org_id.distinct())
            .join(Region, Organization.region_id == Region.region_id)
            .filter(~Region.okrug_id.in_(value))
        )

        return query.filter(Organization.org_id.in_(org_ids))

    def operation(self):
        return lazy_gettext('не в списке')


class OrgDocumentsFilter(filters.FilterInList):
    """Фильтр на список организаций, у которых
    есть организационно-распорядительные документы (любой из списка)."""

    def apply(self, query, value, alias=None):
        return (query
                .join(OrgAdmDocOrganization, Organization.org_adm_doc)
                .filter(OrgAdmDocOrganization.orgadm_id.in_(value))
                )

    def operation(self):
        return lazy_gettext('в списке (логическое ИЛИ)')


class OrgDocumentsAndFilter(filters.FilterInList):
    """Фильтр на список организаций, у которых
    есть организационно-распорядительные документы (каждый из списка)."""

    def apply(self, query, value, alias=None):
        subquery = (
            db.session.query(Organization.org_id)
            .join(OrgAdmDocOrganization, Organization.org_adm_doc)
            .filter(OrgAdmDocOrganization.orgadm_id.in_(value))
            .group_by(Organization.org_id)
            .having(func.count(OrgAdmDocOrganization.orgadm_id) == len(value))
            .all()
        )
        subquery_list_results = [org_id[0] for org_id in subquery]
        return query.filter(Organization.org_id.in_(subquery_list_results))

    def operation(self):
        return lazy_gettext('в списке (логическое И)')


class OrgIsSubjectKIIFilter(filters.BaseSQLAFilter):
    """Фильтр на список организаций,
    чьи ресурсы являются объектами КИИ."""

    def apply(self, query, value, alias=None):
        subjects_kii_ids = (
            db.session
            .query(Organization.org_id.distinct())
            .join(Resource, Organization.resources)
            .filter(Resource.is_okii.is_(True))
        )
        if value == "да":
            return query.filter(Organization.org_id.in_(subjects_kii_ids))
        return query.filter(Organization.org_id.not_in(subjects_kii_ids))

    def operation(self):
        return lazy_gettext('?')

    def get_options(self, view):
        return OPTIONS


class ResourceRegionFilter(filters.FilterInList):
    def apply(self, query, value, alias=None):
        resource_ids = (
            db.session
            .query(Resource.resource_id.distinct())
            .join(Region, Resource.regions)
            .filter(Region.region_id.in_(value))
        )
        return query.filter(Resource.resource_id.in_(resource_ids))


class ResourceIndustryFilter(filters.FilterInList):
    def apply(self, query, value, alias=None):
        resource_ids = (
            db.session
            .query(Resource.resource_id.distinct())
            .join(Industry, Resource.industries)
            .filter(Industry.industry_id.in_(value))
        )
        return query.filter(Resource.resource_id.in_(resource_ids))


class ResourceOkrugFilter(filters.FilterInList):
    def apply(self, query, value, alias=None):
        resource_ids = (
            db.session
            .query(Resource.resource_id.distinct())
            .join(Region, Resource.regions)
            .filter(Region.okrug_id.in_(value))
        )
        return query.filter(Resource.resource_id.in_(resource_ids))


class MessageIsMethodDoc(filters.BaseSQLAFilter):
    """Фильтр на исходящие письма, содержащие
    методические документы."""

    def apply(self, query, value, alias=None):
        subquery_methods = db.session.query(MethodicalDoc.method_id)
        subquery_messages = (db.session
                             .query(Message.message_id)
                             .join(MethodicalDoc, Message.methodical_docs)
                             .filter(MethodicalDoc.method_id
                                     .in_(subquery_methods)
                                     )
                             )
        if value == "да":
            return query.filter(Message.message_id.in_(subquery_messages))
        return query.filter(~Message.message_id.in_(subquery_messages))

    def operation(self):
        return lazy_gettext('равно')

    def get_options(self, view):
        return OPTIONS


class RespResourceRegionFilter(filters.FilterInList):
    def apply(self, query, value, alias=None):
        resps_ids = (
            db.session
            .query(Responsibility.resp_id.distinct())
            .join(Resource, Responsibility.resource)
            .join(Region, Resource.regions)
            .filter(Region.region_id.in_(value))
        )
        return query.filter(Responsibility.resp_id.in_(resps_ids))


class RespResourceOkrugFilter(filters.FilterInList):
    def apply(self, query, value, alias=None):
        resps_ids = (
            db.session
            .query(Responsibility.resp_id.distinct())
            .join(Resource, Responsibility.resource)
            .join(Region, Resource.regions)
            .filter(Region.okrug_id.in_(value))
        )
        return query.filter(Responsibility.resp_id.in_(resps_ids))
