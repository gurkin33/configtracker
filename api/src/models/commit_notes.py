from sqlalchemy.dialects.postgresql import UUID

from api.db import db, TimestampsModel
from respect_validation import Validator as v


class CommitNotesModel(TimestampsModel, db.Model):
    __tablename__ = "commit_notes"

    config_id = db.Column(UUID(as_uuid=True), db.ForeignKey("configs.id"))
    config_bin_id = db.Column(UUID(as_uuid=True), db.ForeignKey("configs_bin.id"))
    commit = db.Column(db.String(40), nullable=False)
    name = db.Column(db.String(256), nullable=False, default="")
    description = db.Column(db.String(4096), nullable=False, default="")

    @classmethod
    def validate(cls, data):
        rules = {
            # 'config_id': v.stringType().notEmpty(),
            # 'commit': v.stringType().notEmpty().length(max_value=40),
            'name': v.Optional(v.stringType().length(max_value=256)),
            'description': v.Optional(v.stringType().length(max_value=4096)),
        }

        return cls.fv().validate(data, rules)

    def get(self):
        item = {}
        for c in self.__table__.columns.keys():
            if c in ['config_id', 'config_bin_id', 'commit']:
                continue
            item[c] = self._output_serialization(getattr(self, c))
        return item

    @classmethod
    def find_(cls, config_id: str, commit: str, bin_: bool = False):
        if bin_:
            return cls.query.filter_by(config_bin_id=config_id, commit=commit).first()
        else:
            return cls.query.filter_by(config_id=config_id, commit=commit).first()

    @classmethod
    def save_data(cls, config_id: str, commit: str, data: dict, bin_: bool = False):
        if bin_:
            notes = cls.query.filter_by(config_bin_id=config_id, commit=commit).first()
        else:
            notes = cls.query.filter_by(config_id=config_id, commit=commit).first()
        data['commit'] = commit
        if not notes:
            if bin_:
                data['config_bin_id'] = config_id
            else:
                data['config_id'] = config_id
            notes = cls(**data)
        else:
            notes.name = data['name'] if 'name' in data.keys() else notes.name
            notes.description = data['description'] if 'description' in data.keys() else notes.description

        notes.save()

        return notes

    @classmethod
    def move_to_bin(cls, config_id: str, config_bin_id: str):
        notes_ = cls.query.filter_by(config_id=config_id).all()
        for n in notes_:
            n.config_id = None
            n.config_bin_id = config_bin_id
            n.save()
        # may be better to use session flush + commit:
        # https://docs.sqlalchemy.org/en/20/_modules/examples/performance/bulk_updates.html
        # check later
