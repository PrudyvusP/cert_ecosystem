from ..extentions import db

industries_resources_table = db.Table(
    "industries_resources",
    db.Column("industry_id",
              db.Integer,
              db.ForeignKey("industries.industry_id",
                            ondelete="CASCADE")
              ),
    db.Column("resource_id",
              db.Integer,
              db.ForeignKey("resources.resource_id",
                            ondelete="CASCADE")
              )
)
