from ..extentions import db
from .responsibility_service import responsibilities_services_table


class Service(db.Model):
    """Модель услуги в области информационной безопасности."""
    __tablename__ = "services"

    service_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    responsibilities = db.relationship(
        "Responsibility",
        secondary=responsibilities_services_table,
        back_populates="services",
        order_by='Responsibility.date_start'
    )

    def __repr__(self):
        return self.name
