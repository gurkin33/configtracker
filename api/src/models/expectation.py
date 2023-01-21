from sqlalchemy.dialects.postgresql import UUID

from api.db import db, UuidModel
from respect_validation import Validator as v


class ExpectationModel(UuidModel, db.Model):
    __tablename__ = "expectations"

    script_id = db.Column(UUID(as_uuid=True), db.ForeignKey("scripts_expect.id"))
    prompt = db.Column(db.String(256), nullable=False, default="")
    cmd = db.Column(db.String(1024), nullable=False)
    timeout = db.Column(db.Integer(), nullable=False, default=0)
    save = db.Column(db.Boolean(), nullable=False, default=False)
    order = db.Column(db.Integer(), nullable=False, default=0)
    secret = db.Column(db.Boolean(), nullable=False, default=False)
    skip_top = db.Column(db.Integer(), nullable=False, default=0)
    skip_bottom = db.Column(db.Integer(), nullable=False, default=0)

    @classmethod
    def validate(cls, exception, _id: str = ''):
        rules = {
            'id': v.Optional(v.stringType().notEmpty()),
            'script_id': v.Optional(v.stringType()),
            'prompt': v.stringType().length(max_value=256),
            'cmd': v.stringType().notEmpty().length(max_value=1024).set_name('Command'),
            'timeout': v.intType().between(0, 600),
            'save': v.boolType(),
            'secret': v.boolType(),
            'order': v.intType().between(0, 300),
            'skip_top': v.Optional(v.intType().between(0, 600)),
            'skip_bottom': v.Optional(v.intType().between(0, 600))
        }

        return cls.fv().validate(exception, rules)

    def get(self):
        item = {}
        for c in self.__table__.columns.keys():
            if c in ['id', 'script_id']:
                continue
            item[c] = self._output_serialization(getattr(self, c))
        # if item['secret']:
        #     item['command'] = '__SECRET_COMMAND__'
        return item

    def get_config(self):
        item = {}
        for c in self.__table__.columns.keys():
            if c in ["id", "script_id"]:
                continue
            if c in ["prompt"]:
                prompts = self._output_serialization(getattr(self, c))
                item[c] = prompts.split(",") if prompts else []
                continue
            item[c] = self._output_serialization(getattr(self, c))
        return item

    @staticmethod
    def bulk_insert(objects):
        db.session.add_all(objects)
        db.session.commit()
