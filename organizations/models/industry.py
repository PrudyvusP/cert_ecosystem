from .industry_resource import industries_resources_table
from ..extentions import db


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
