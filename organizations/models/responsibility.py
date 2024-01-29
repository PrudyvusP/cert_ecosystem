from ..extentions import db


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
