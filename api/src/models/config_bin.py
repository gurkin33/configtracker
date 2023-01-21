from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.db import TimestampsModel, db
from api.src.models.config_git_parent import ConfigGitParent


class ConfigBinModel(ConfigGitParent, TimestampsModel, db.Model):
    __tablename__ = 'configs_bin'

    name = db.Column(db.String(256), nullable=False)
    size = db.Column(db.Integer(), nullable=True, default=None)
    last_modification = db.Column(db.TIMESTAMP(), nullable=True, default=None)

    address = db.Column(db.String(256), nullable=False)
    username = db.Column(db.String(256), nullable=False)
    protocol = db.Column(db.String(256), nullable=False)

    repo_id = db.Column(UUID(as_uuid=True), db.ForeignKey("repositories.id"), nullable=False)

    style = db.Column(db.String(1024), unique=False, nullable=True, default="")
    icon = db.Column(db.String(1024), unique=False, nullable=True, default="")

    commit_notes = relationship("CommitNotesModel", backref="config_bin_notes", cascade="all,delete")

    relationships = ['repo']
    additional_table_columns = ['repo']

    def get(self):
        item = {}
        for c in self.__table__.columns.keys():
            item[c] = self._output_serialization(getattr(self, c))

        return item
