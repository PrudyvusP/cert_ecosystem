from ..extentions import db

organizations_messages = db.Table(
    "organizations_messages",
    db.Column("org_id",
              db.Integer,
              db.ForeignKey("organizations.org_id",
                            ondelete="CASCADE")
              ),
    db.Column("message_id",
              db.Integer,
              db.ForeignKey("messages.message_id",
                            ondelete="CASCADE")
              )
)
