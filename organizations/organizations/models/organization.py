from datetime import datetime

from sqlalchemy.sql import false

from ..extentions import db
from ..utils import (generate_uuid, get_alpha_num_string,
                     get_string_wo_special_symbols)
from .mixins import DateAddedCreatedMixin
from .organization_message import organizations_messages


class Organization(DateAddedCreatedMixin, db.Model):
    """Модель организации."""
    __tablename__ = "organizations"

    date_added = db.Column(db.DateTime, nullable=False,
                           default=datetime.today)
    date_updated = db.Column(db.DateTime, default=datetime.today,
                             onupdate=datetime.today)
    org_id = db.Column(db.Integer, primary_key=True)

    db_name = db.Column(db.Text, nullable=False, index=True)
    full_name = db.Column(db.Text, nullable=False)
    short_name = db.Column(db.Text)
    inn = db.Column(db.String(10), index=True)
    kpp = db.Column(db.String(9), index=True)
    ogrn = db.Column(db.String(13), index=True)
    factual_address = db.Column(db.Text)
    mailing_address = db.Column(db.Text, nullable=True)
    boss_position = db.Column(db.String(200))
    boss_fio = db.Column(db.String(200))
    contacts = db.Column(db.Text)
    date_agreement = db.Column(db.Date, index=True)
    agreement_unit = db.Column(db.Text)
    is_gov = db.Column(db.Boolean, default=False)
    is_military = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_250 = db.Column(db.Boolean, server_default=false(), default=False)

    uuid = db.Column(db.String(36), default=generate_uuid,
                     unique=True)

    region_id = db.Column(db.Integer,
                          db.ForeignKey("regions.region_id",
                                        ondelete="SET NULL")
                          )

    region = db.relationship("Region", backref="organizations")

    soft_delete_condition = ("and_(Organization.org_id==Resource.org_id,"
                             " Resource.is_active==True)")

    resources = db.relationship("Resource",
                                backref="org_owner",
                                passive_deletes=True,
                                primaryjoin=soft_delete_condition,
                                order_by="Resource.name")

    com_contacts = db.relationship("Contact",
                                   backref="from_org",
                                   lazy='dynamic',
                                   passive_deletes=True)

    org_adm_doc = db.relationship("OrgAdmDocOrganization",
                                  back_populates="organization",
                                  cascade="all, delete")

    messages = db.relationship("Message",
                               secondary=organizations_messages,
                               back_populates="organizations",
                               cascade="all, delete",
                               order_by="desc(Message.datetime_created)",
                               )
    certs = db.relationship("Cert",
                            backref="org_owner")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_name = get_alpha_num_string(kwargs.get('full_name'))
        self.short_name = kwargs.get('short_name').upper() if kwargs.get(
            'short_name') else None
        self.full_name = kwargs.get('full_name')

    @property
    def first_two_uuid_symb(self):
        return self.uuid[:2].upper()

    def get_org_dir_name(self):
        return get_string_wo_special_symbols(self.short_name[:60])

    def __repr__(self):
        name = self.full_name[:100]
        if self.inn or self.kpp:
            return f"{name} (ИНН/КПП {self.inn}/{self.kpp})"
        return name
