from ..extentions import db


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
