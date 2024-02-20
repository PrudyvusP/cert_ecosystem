from .mixins import DateAddedCreatedMixin
from ..extentions import db


class Contact(DateAddedCreatedMixin, db.Model):
    """Модель контакта по взаимодействию."""
    __tablename__ = "contacts"

    contact_id = db.Column(db.Integer, primary_key=True)

    fio = db.Column(db.String(254))
    dep = db.Column(db.String(254))
    pos = db.Column(db.String(254))
    mob_phone = db.Column(db.String(20))
    work_phone = db.Column(db.String(20))
    email = db.Column(db.String(254))
    is_main = db.Column(db.Boolean, default=False)

    org_id = db.Column(db.Integer,
                       db.ForeignKey("organizations.org_id",
                                     ondelete="CASCADE"),
                       nullable=False)

    def __repr__(self):
        return self.fio
