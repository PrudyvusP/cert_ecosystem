from datetime import datetime

from sqlalchemy.orm import backref

from .organization_message import organizations_messages
from .methodicaldoc_message import methodicaldocs_messages
from ..extentions import db


class Message(db.Model):
    """Модель письма организации."""
    __tablename__ = "messages"
    message_id = db.Column(db.Integer, primary_key=True)

    date_inbox_approved = db.Column(db.Date)
    number_inbox_approved = db.Column(db.String(70))

    date_registered = db.Column(db.Date)
    our_inbox_number = db.Column(db.String(70))

    date_approved = db.Column(db.Date)
    our_outbox_number = db.Column(db.String(70))

    information = db.Column(db.Text, nullable=False)

    datetime_created = db.Column(db.DateTime, default=datetime.today)
    datetime_updated = db.Column(db.DateTime, onupdate=datetime.today)

    is_inbox = db.Column(db.Boolean, default=True)

    methodical_docs = db.relationship("MethodicalDoc",
                                      secondary=methodicaldocs_messages,
                                      back_populates="messages",
                                      order_by='MethodicalDoc.name'
                                      )

    organizations = db.relationship("Organization",
                                    secondary=organizations_messages,
                                    back_populates="messages",
                                    passive_deletes=True,
                                    order_by="Organization.full_name")

    parent_id = db.Column(db.Integer,
                          db.ForeignKey("messages.message_id")
                          )
    children = db.relationship("Message",
                               backref=backref('parent',
                                               remote_side=[message_id])
                               )

    def __repr__(self):
        if self.is_inbox:
            return (f'Вх. № {self.our_inbox_number}'
                    f' (№ {self.number_inbox_approved} от'
                    f' {self.date_inbox_approved})')
        return (f'Исх. № {self.our_outbox_number}'
                f' от {self.date_approved}')
