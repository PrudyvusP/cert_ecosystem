from ..extentions import db

regions_resources_table = db.Table(
    "regions_resources",
    db.Column("region_id",
              db.Integer,
              db.ForeignKey("regions.region_id",
                            ondelete="CASCADE")
              ),
    db.Column("resource_id",
              db.Integer,
              db.ForeignKey("resources.resource_id",
                            ondelete="CASCADE")
              )
)
