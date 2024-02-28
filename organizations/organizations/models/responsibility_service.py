from ..extentions import db

responsibilities_services_table = db.Table(
    "responsibilities_services",
    db.Column("service_id",
              db.Integer,
              db.ForeignKey("services.service_id",
                            ondelete="CASCADE")
              ),
    db.Column("resp_id",
              db.Integer,
              db.ForeignKey("responsibilities_with_certs.resp_id",
                            ondelete="CASCADE")
              )
)
