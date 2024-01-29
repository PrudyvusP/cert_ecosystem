from flask_sqlalchemy import BaseQuery

from .industry_resource import industries_resources_table
from .mixins import DateAddedCreatedMixin
from .regions_resource import regions_resources_table
from ..extentions import db
from ..utils import generate_uuid


class ModelWithSoftDelete(BaseQuery):
    """Модель-конструктор запросов для поддержки
    технологии мягкого удаления с флажком is_active."""

    def __new__(cls, *args, **kwargs):
        obj = super(ModelWithSoftDelete, cls).__new__(cls)
        obj._with_deleted = kwargs.pop('_with_deleted', False)
        if args:
            super(ModelWithSoftDelete, obj).__init__(*args, **kwargs)
            if obj._with_deleted:
                return obj
        return obj.filter_by(is_active=True)

    def __init__(self, *args, **kwargs):
        pass

    def with_deleted(self):
        return self.__class__(self._only_full_mapper_zero('get'),
                              session=db.session(), _with_deleted=True)

    def _get(self, *args, **kwargs):
        return super(ModelWithSoftDelete, self).get(*args, **kwargs)

    def get(self, *args, **kwargs):
        obj = self.with_deleted()._get(*args, **kwargs)
        return (obj if obj is None or self._with_deleted or obj.is_active
                else None)


class Resource(DateAddedCreatedMixin, db.Model):
    """Модель информационного ресурса."""
    query_class = ModelWithSoftDelete

    __tablename__ = "resources"
    resource_id = db.Column(db.Integer, primary_key=True)

    is_okii = db.Column(db.Boolean, default=False)
    fstec_reg_number = db.Column(db.String(15))
    name = db.Column(db.Text, nullable=False)
    category = db.Column(db.SmallInteger, index=True)
    date_added_to_fstec = db.Column(db.Date)
    date_updated_to_fstec = db.Column(db.Date)
    factual_addresses = db.Column(db.Text)
    resp_worker = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    ip_pool = db.Column(db.Text)
    dns_pool = db.Column(db.Text)

    uuid = db.Column(db.String(36), default=generate_uuid,
                     unique=True)

    org_id = db.Column(db.Integer,
                       db.ForeignKey("organizations.org_id",
                                     ondelete="SET NULL"),
                       nullable=False)

    regions = db.relationship("Region",
                              secondary=regions_resources_table,
                              back_populates="resources",
                              cascade="all, delete",
                              order_by="Region.name")

    industries = db.relationship("Industry",
                                 secondary=industries_resources_table,
                                 back_populates="resources",
                                 cascade="all, delete",
                                 )

    outsource_org = db.relationship("Responsibility",
                                    back_populates="resource",
                                    passive_deletes=True
                                    )

    def __repr__(self):
        return f"{self.fstec_reg_number}# {self.name[0:30]}"
