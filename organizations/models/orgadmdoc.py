from .mixins import DateAddedCreatedMixin
from ..extentions import db


class OrgAdmDoc(DateAddedCreatedMixin, db.Model):
    """Модель организационно-распорядительного документа организации."""
    __tablename__ = "orgadm_docs"
    orgadm_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)

    name_prefix = db.Column(db.String(50), nullable=False)

    organization = db.relationship("OrgAdmDocOrganization",
                                   back_populates="org_doc",
                                   passive_deletes=True)

    is_main = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return self.name[:80]
