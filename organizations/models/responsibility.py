from .responsibility_service import responsibilities_services_table
from ..extentions import db


class Responsibility(db.Model):
    """Дополнительная модель для хранения информации
    об аутсорсинге ИБ-услуг ресурсам."""

    __tablename__ = "responsibilities_with_certs"
    resp_id = db.Column(db.Integer, primary_key=True, unique=True)

    cert_id = db.Column(
        db.Integer,
        db.ForeignKey("certs.cert_id",
                      ondelete="CASCADE"),
        nullable=False
    )
    resource_id = db.Column(
        db.Integer,
        db.ForeignKey("resources.resource_id",
                      ondelete="CASCADE"),
        nullable=False
    )

    date_start = db.Column(db.Date, nullable=False, index=True)
    date_end = db.Column(db.Date, nullable=False, index=True)
    type = db.Column(db.String(200))
    props = db.Column(db.Text)
    comment = db.Column(db.Text)

    cert = db.relationship("Cert", back_populates="responsible_units")
    resource = db.relationship("Resource",
                               back_populates="outsource_org")

    services = db.relationship("Service",
                               secondary=responsibilities_services_table,
                               back_populates="responsibilities",
                               order_by='Service.name'
                               )

    def __repr__(self):
        return f"{self.resource} + {self.cert}"
