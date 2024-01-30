from .mixins import DateAddedCreatedMixin
from .organization_message import organizations_messages
from ..extentions import db
from ..utils import (generate_uuid, get_alpha_num_string,
                     get_string_wo_special_symbols)


class Organization(DateAddedCreatedMixin, db.Model):
    """Модель организации."""
    __tablename__ = "organizations"
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

    uuid = db.Column(db.String(36), default=generate_uuid,
                     unique=True)

    region_id = db.Column(db.Integer,
                          db.ForeignKey("regions.region_id",
                                        ondelete="SET NULL")
                          )

    soft_delete_condition = ("and_(Organization.org_id==Resource.org_id,"
                             " Resource.is_active==True)")

    resources = db.relationship("Resource",
                                backref="org_owner",
                                passive_deletes=True,
                                primaryjoin=soft_delete_condition,
                                order_by="Resource.fstec_reg_number,"
                                         "Resource.name")

    com_contacts = db.relationship("Contact",
                                   backref="from_org",
                                   passive_deletes=True,
                                   order_by="desc(Contact.is_main)")

    responsible_unit = db.relationship("Responsibility",
                                       back_populates="organization",
                                       cascade="all, delete")

    org_adm_doc = db.relationship("OrgAdmDocOrganization",
                                  back_populates="organization",
                                  cascade="all, delete")

    messages = db.relationship("Message",
                               secondary=organizations_messages,
                               back_populates="organizations",
                               cascade="all, delete",
                               order_by="desc(Message.datetime_created)",
                               )

    def __init__(self, full_name, short_name=None, ogrn=None, inn=None,
                 factual_address=None, boss_position=None, boss_fio=None,
                 contacts=None, date_agreement=None, agreement_unit=None,
                 is_gov=False, is_military=False,
                 is_active=True, region=None, kpp=None):
        self.full_name = full_name.upper()
        self.short_name = short_name.upper()
        self.ogrn = ogrn
        self.inn = inn
        self.kpp = kpp
        self.factual_address = factual_address
        self.boss_position = boss_position
        self.boss_fio = boss_fio
        self.contacts = contacts
        self.date_agreement = date_agreement
        self.agreement_unit = agreement_unit
        self.is_gov = is_gov
        self.is_military = is_military
        self.is_active = is_active
        self.region = region

        self.db_name = get_alpha_num_string(full_name)

    @property
    def first_two_uuid_symb(self):
        return self.uuid[:2].upper()

    def get_org_dir_name(self):
        return get_string_wo_special_symbols(self.short_name[:60])

    def __repr__(self):
        name = self.full_name[:88]
        if self.inn or self.kpp:
            return f"{name} (ИНН/КПП {self.inn}/{self.kpp})"
        return name
