from .mixins import DateAddedCreatedMixin
from ..extentions import db
from ..utils import generate_uuid


class Cert(DateAddedCreatedMixin, db.Model):
    """Модель центра мониторинга."""

    __tablename__ = "certs"
    cert_id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.Text, nullable=False)
    uuid = db.Column(db.String(36), default=generate_uuid,
                     unique=True)
    type = db.Column(db.String(1), nullable=True)
    date_actual_resp = db.Column(db.Date, nullable=True)

    org_id = db.Column(db.Integer,
                       db.ForeignKey("organizations.org_id",
                                     ondelete="SET NULL"))

    def __repr__(self):
        return self.name
