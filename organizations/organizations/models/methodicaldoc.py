from io import BytesIO

from ..extentions import db
from .methodicaldoc_message import methodicaldocs_messages
from .mixins import DateAddedCreatedMixin


class MethodicalDoc(DateAddedCreatedMixin, db.Model):
    """Модель методического документа."""
    __tablename__ = "methodical_docs"
    method_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    short_name = db.Column(db.Text)
    name_for_letter = db.Column(db.Text)
    date_approved = db.Column(db.Date)
    props = db.Column(db.Text)
    path_prefix = db.Column(db.Text, nullable=False)
    is_conf = db.Column(db.Boolean, nullable=False,
                        default=False)
    is_active = db.Column(db.Boolean, nullable=False,
                          default=True)
    data = db.Column(db.LargeBinary)
    data_extension = db.Column(db.String(10))

    messages = db.relationship("Message",
                               secondary=methodicaldocs_messages,
                               back_populates="methodical_docs",
                               passive_deletes=True
                               )

    def __repr__(self):
        return self.name[:40]

    @property
    def get_file(self):
        return BytesIO(self.data)

    @property
    def get_file_name(self):
        if self.data_extension:
            return self.short_name + self.data_extension
        return 'file.pdf'
