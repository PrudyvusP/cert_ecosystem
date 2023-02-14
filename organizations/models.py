from datetime import date, datetime
from io import BytesIO

from flask_sqlalchemy import BaseQuery
from sqlalchemy.orm import backref

from .extentions import db
from .utils import (generate_uuid, get_alpha_num_string,
                    get_quick_query_count,
                    get_string_wo_special_symbols)

regions_resources_table = db.Table(
    "regions_resources",
    db.Column("region_id",
              db.Integer,
              db.ForeignKey("regions.region_id",
                            ondelete="CASCADE")
              ),
    db.Column("resource_id",
              db.Integer,
              db.ForeignKey("resources.resource_id",
                            ondelete="CASCADE")
              )
)

industries_resources_table = db.Table(
    "industries_resources",
    db.Column("industry_id",
              db.Integer,
              db.ForeignKey("industries.industry_id",
                            ondelete="CASCADE")
              ),
    db.Column("resource_id",
              db.Integer,
              db.ForeignKey("resources.resource_id",
                            ondelete="CASCADE")
              )
)

methodicaldocs_messages = db.Table(
    "methodicaldocs_messages",
    db.Column("method_id",
              db.Integer,
              db.ForeignKey("methodical_docs.method_id",
                            ondelete="CASCADE")
              ),
    db.Column("message_id",
              db.Integer,
              db.ForeignKey("messages.message_id",
                            ondelete="CASCADE")
              )
)

organizations_messages = db.Table(
    "organizations_messages",
    db.Column("org_id",
              db.Integer,
              db.ForeignKey("organizations.org_id",
                            ondelete="CASCADE")
              ),
    db.Column("message_id",
              db.Integer,
              db.ForeignKey("messages.message_id",
                            ondelete="CASCADE")
              )
)


class DateAddedCreatedMixin:
    """Миксин для моделей, создание и изменение
     которых необходимо отслеживать."""
    date_added = db.Column(db.Date, nullable=False, default=date.today)
    date_updated = db.Column(db.Date, default=date.today, onupdate=date.today)


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
    def is_subject_kii(self):
        return get_quick_query_count(
            (db.session.query(Resource.resource_id)
             .join(Resource, Organization.resources)
             .filter(Organization.org_id == self.org_id,
                     Resource.is_okii.is_(True)
                     )
             )
        ) > 0

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


class Message(db.Model):
    """Модель письма организации."""
    __tablename__ = "messages"
    message_id = db.Column(db.Integer, primary_key=True)

    date_inbox_approved = db.Column(db.Date)
    number_inbox_approved = db.Column(db.String(70))

    date_registered = db.Column(db.Date)
    our_inbox_number = db.Column(db.String(70))

    date_approved = db.Column(db.Date)
    our_outbox_number = db.Column(db.String(70))

    information = db.Column(db.Text, nullable=False)

    datetime_created = db.Column(db.DateTime, default=datetime.today)
    datetime_updated = db.Column(db.DateTime, onupdate=datetime.today)

    is_inbox = db.Column(db.Boolean, default=True)

    methodical_docs = db.relationship("MethodicalDoc",
                                      secondary=methodicaldocs_messages,
                                      back_populates="messages",
                                      order_by='MethodicalDoc.name'
                                      )

    organizations = db.relationship("Organization",
                                    secondary=organizations_messages,
                                    back_populates="messages",
                                    passive_deletes=True,
                                    order_by="Organization.full_name")

    parent_id = db.Column(db.Integer,
                          db.ForeignKey("messages.message_id")
                          )
    children = db.relationship("Message",
                               backref=backref('parent',
                                               remote_side=[message_id])
                               )

    def __repr__(self):
        if self.is_inbox:
            return (f'Вх. № {self.our_inbox_number}'
                    f' (№ {self.number_inbox_approved} от'
                    f' {self.date_inbox_approved})')
        return (f'Исх. № {self.our_outbox_number}'
                f' от {self.date_approved}')


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


class Responsibility(db.Model):
    """Дополнительная модель для хранения информации
    об аутсорсинге ИБ-услуг ресурсам."""
    __tablename__ = "responsibilities"

    org_id = db.Column(
        db.Integer,
        db.ForeignKey("organizations.org_id",
                      ondelete="CASCADE"),
        primary_key=True
    )
    resource_id = db.Column(
        db.Integer,
        db.ForeignKey("resources.resource_id",
                      ondelete="CASCADE"),
        primary_key=True
    )

    date_start = db.Column(db.Date, nullable=False, index=True)
    date_end = db.Column(db.Date, nullable=False,
                         primary_key=True, index=True)
    props = db.Column(db.Text)
    comment = db.Column(db.Text)

    organization = db.relationship("Organization",
                                   back_populates="responsible_unit")
    resource = db.relationship("Resource",
                               back_populates="outsource_org")

    def __repr__(self):
        return f"#{self.resource.name} by {self.organization.short_name}"


class Industry(db.Model):
    """Модель сферы деятельности информационного ресурса."""
    __tablename__ = "industries"
    industry_id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.Text, nullable=False)

    resources = db.relationship("Resource",
                                secondary=industries_resources_table,
                                back_populates="industries",
                                passive_deletes=True)

    def __repr__(self):
        return self.name


class Region(db.Model):
    """Модель региона."""
    __tablename__ = "regions"
    region_id = db.Column(db.Integer, primary_key=True, nullable=False)

    name = db.Column(db.String(70), nullable=False)

    okrug_id = db.Column(db.Integer,
                         db.ForeignKey("okrugs.okrug_id",
                                       ondelete="SET NULL")
                         )

    organizations = db.relationship("Organization",
                                    backref="region",
                                    passive_deletes=True)

    addresses = db.relationship("Address",
                                backref="region",
                                passive_deletes=True)

    resources = db.relationship("Resource",
                                secondary=regions_resources_table,
                                back_populates="regions",
                                passive_deletes=True)

    def __repr__(self):
        return self.name


class Okrug(db.Model):
    """Модель округа."""
    __tablename__ = "okrugs"
    okrug_id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(20))

    regions = db.relationship("Region",
                              backref="okrug",
                              passive_deletes=True)

    def __repr__(self):
        return self.name


class Address(db.Model):
    """Модель адреса почтового отделения."""
    __tablename__ = "addresses"
    index = db.Column(db.String(6), primary_key=True, nullable=False)

    area = db.Column(db.String(40))
    locality = db.Column(db.String(60), index=True)

    region_id = db.Column(db.Integer,
                          db.ForeignKey("regions.region_id",
                                        ondelete="SET NULL"))

    def __repr__(self):
        return f"{str(self.index)}# {self.area}"


class MethodicalDoc(DateAddedCreatedMixin, db.Model):
    """Модель методического документа."""
    __tablename__ = "methodical_docs"
    method_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    short_name = db.Column(db.Text)
    date_approved = db.Column(db.Date)
    props = db.Column(db.Text)
    path_prefix = db.Column(db.Text, nullable=False)
    is_conf = db.Column(db.Boolean, nullable=False,
                        default=False)
    is_active = db.Column(db.Boolean, nullable=False,
                          default=True)
    data = db.Column(db.LargeBinary)
    data_extension = db.Column(db.String(10))

    messages = db.relationship("Message",
                               secondary=methodicaldocs_messages,
                               back_populates="methodical_docs",
                               passive_deletes=True
                               )

    def __repr__(self):
        return self.name[:40]

    @property
    def get_file(self):
        return BytesIO(self.data)

    @property
    def get_file_name(self):
        if self.data_extension:
            return self.short_name + self.data_extension
        return 'file.pdf'


class OrgAdmDoc(DateAddedCreatedMixin, db.Model):
    """Модель организационно-распорядительного документа организации."""
    __tablename__ = "orgadm_docs"
    orgadm_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)

    name_prefix = db.Column(db.String(50), nullable=False)

    organization = db.relationship("OrgAdmDocOrganization",
                                   back_populates="org_doc",
                                   passive_deletes=True)

    def __repr__(self):
        return self.name[:80]


class OrgAdmDocOrganization(db.Model):
    """Дополнительная модель для связи организаций и их
    организационно-распорядительных документов."""
    __tablename__ = "orgadmdocs_organizations"

    org_id = db.Column(
        db.Integer,
        db.ForeignKey("organizations.org_id",
                      ondelete="CASCADE"),
        primary_key=True
    )
    orgadm_id = db.Column(
        db.Integer,
        db.ForeignKey('orgadm_docs.orgadm_id',
                      ondelete="CASCADE"),
        primary_key=True
    )

    date_approved = db.Column(db.Date)
    props = db.Column(db.Text)
    our_inbox_number = db.Column(db.String(7))
    inventory_number = db.Column(db.Integer)
    comment = db.Column(db.Text)
    organization = db.relationship("Organization",
                                   back_populates="org_adm_doc")

    org_doc = db.relationship("OrgAdmDoc",
                              back_populates="organization")

    def __repr__(self):
        return f"{self.organization.short_name}'s document {self.org_doc.name}"
