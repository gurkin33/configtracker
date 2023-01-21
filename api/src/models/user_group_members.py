from api.db import db

UserGroupMembers = db.Table(
    "user_group_members",
    db.metadata,
    db.Column("user_id", db.ForeignKey("users.id")),
    db.Column("user_group_id", db.ForeignKey("user_groups.id")),
)