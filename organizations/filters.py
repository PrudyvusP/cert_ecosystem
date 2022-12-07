from flask_admin.babel import lazy_gettext
from flask_admin.contrib.sqla import filters

from .extentions import db
from .models import (Organization, Resource,
                     Region, Message, Responsibility,
                     OrgAdmDocOrganization, Industry, Okrug)

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
        return (query
                .join(Region, Organization.region)
                .filter(Organization.region_id.in_(value))
                )


class OrgOkrugFilter(filters.FilterInList):
    """Фильтр на список организаций,
    расположенных в округах, id которых переданы."""
    def apply(self, query, value, alias=None):
        return (query
                .join(Region, Organization.region_id == Region.region_id)
                .join(Okrug, Region.okrug_id == Okrug.okrug_id)
                .filter(Region.okrug_id.in_(value))
                )

class OrgDocumentsFilter(filters.FilterInList):
    """Фильтр на список организаций, у которых
    есть организационно-распорядительные документы."""
    def apply(self, query, value, alias=None):
        return (query
                .join(OrgAdmDocOrganization,
                      Organization.org_id == OrgAdmDocOrganization.org_id)
                .filter(OrgAdmDocOrganization.orgadm_id.in_(value))
                )


class OrgIsSubjectKIIFilter(filters.BaseSQLAFilter):
    """Фильтр на список организаций,
    чьи ресурсы являются объектами КИИ."""

    def apply(self, query, value, alias=None):
        subjects_kii_ids = (
            db.session.query(
                Organization.org_id.distinct()
            ).join(Resource, Organization.resources)
            .filter(Resource.is_okii.is_(True)
                    )
        )
        if value == "да":
            return query.filter(Organization.org_id.in_(subjects_kii_ids))
        return query.filter(Organization.org_id.not_in(subjects_kii_ids))

    def operation(self):
        return lazy_gettext('?')

    def get_options(self, view):
        return OPTIONS


class OrgHasHadAnyContactsWithUsFilter(filters.BaseSQLAFilter):
    """Фильтр на список организаций,
    с которыми было взаимодействие или не было такового."""

    def apply(self, query, value, alias=None):
        orgs_with_messages = (db.session
                              .query(Organization.org_id)
                              .join(Message, Organization.messages)
                              )
        orgs_with_resources = (db.session
                               .query(Organization.org_id)
                               .join(Resource, Organization.resources)
                               )
        orgs_with_documents = (
            db.session.query(OrgAdmDocOrganization.org_id)
        )
        orgs_with_responsibility = (
            db.session.query(Responsibility.org_id)
        )
        final_query = (orgs_with_messages.union(orgs_with_resources,
                                                orgs_with_documents,
                                                orgs_with_responsibility)
                       .all()
                       )
        final_query = set(i for i, in final_query)
        if value == 'да':
            return (query
                    .filter(Organization.org_id.in_(final_query))
                    .order_by(Organization.full_name)
                    )
        return (query
                .filter(Organization.org_id.not_in(final_query))
                .order_by(Organization.full_name)
                )

    def operation(self):
        return lazy_gettext('?')

    def get_options(self, view):
        return OPTIONS


class ResourceRegionFilter(filters.FilterInList):
    def apply(self, query, value, alias=None):
        return (query
                .join(Region, Resource.regions)
                .filter(Region.region_id.in_(value)
                        )
                )


class ResourceIndustryFilter(filters.FilterInList):
    def apply(self, query, value, alias=None):
        return (query
                .join(Industry, Resource.industries)
                .filter(Industry.industry_id.in_(value)
                        )
                )


class ResourceOkrugFilter(filters.FilterInList):
    def apply(self, query, value, alias=None):
        return (query
                .join(Region, Resource.regions)
                .join(Okrug, Region.okrug)
                .filter(Region.okrug_id.in_(value)
                        )
                )
