from .industry_resource import industries_resources_table
from .mixins import DateAddedCreatedMixin
from .regions_resource import regions_resources_table
from ..extentions import db
from ..utils import generate_uuid


class Resource(DateAddedCreatedMixin, db.Model):
    """Модель информационного ресурса."""

    __tablename__ = "resources"
    resource_id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.Text, nullable=False)

    is_okii = db.Column(db.Boolean, default=False)
    fstec_reg_number = db.Column(db.String(15))
    category = db.Column(db.SmallInteger, nullable=True)

    factual_addresses = db.Column(db.Text)

    date_added_to_fstec = db.Column(db.Date)
    date_updated_to_fstec = db.Column(db.Date)

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
        return f"{self.name[0:50]}"
