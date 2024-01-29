from ..extentions import db


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
