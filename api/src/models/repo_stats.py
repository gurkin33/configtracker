from sqlalchemy.dialects.postgresql import UUID

from api.db import db, UuidModel


class RepoStatsModel(UuidModel, db.Model):
    __tablename__ = 'repo_stats'

    repo_id = db.Column(UUID(as_uuid=True), db.ForeignKey("repositories.id"))
    # repo = relationship("RepositoryModel", cascade="all,delete", backref="repo_stats")
    date = db.Column(db.TIMESTAMP, nullable=False)
    files_changed = db.Column(db.Integer(), nullable=False, default=0)
    insertions = db.Column(db.Integer(), nullable=False, default=0)
    deletions = db.Column(db.Integer(), nullable=False, default=0)

    def get(self):
        item = {}
        for c in self.__table__.columns.keys():
            if c in ['id', 'repo_id']:
                continue
            item[c] = self._output_serialization(getattr(self, c))
        return item