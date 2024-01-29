from .regions_resource import regions_resources_table
from ..extentions import db


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
