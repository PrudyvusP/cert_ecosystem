from ..extentions import db


class OrgAdmDocOrganization(db.Model):
    """Дополнительная модель для связи организаций и их
    организационно-распорядительных документов."""
    __tablename__ = "orgadmdocs_organizations"

    org_id = db.Column(
        db.Integer,
        db.ForeignKey("organizations.org_id",
                      ondelete="CASCADE"),
        primary_key=True
    )
    orgadm_id = db.Column(
        db.Integer,
        db.ForeignKey('orgadm_docs.orgadm_id',
                      ondelete="CASCADE"),
        primary_key=True
    )

    date_approved = db.Column(db.Date)
    props = db.Column(db.Text)
    our_inbox_number = db.Column(db.String(7))
    inventory_number = db.Column(db.Integer)
    comment = db.Column(db.Text)
    organization = db.relationship("Organization",
                                   back_populates="org_adm_doc")

    org_doc = db.relationship("OrgAdmDoc",
                              back_populates="organization")

    def __repr__(self):
        return f"{self.organization.short_name}'s document {self.org_doc.name}"
