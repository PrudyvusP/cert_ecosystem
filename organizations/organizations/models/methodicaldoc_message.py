from ..extentions import db

methodicaldocs_messages = db.Table(
    "methodicaldocs_messages",
    db.Column("method_id",
              db.Integer,
              db.ForeignKey("methodical_docs.method_id",
                            ondelete="CASCADE")
              ),
    db.Column("message_id",
              db.Integer,
              db.ForeignKey("messages.message_id",
                            ondelete="CASCADE")
              )
)
