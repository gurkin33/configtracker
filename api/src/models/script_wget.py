from typing import Dict, Any

from api.db import db, UuidModel
from respect_validation import Validator as v


class ScriptWgetModel(UuidModel, db.Model):
    __tablename__ = 'scripts_wget'

    link = db.Column(db.String(512), nullable=False)
    timeout = db.Column(db.Integer(), nullable=False, default=60)

    @classmethod
    def validate(cls, script_wget, _id: str = ''):
        rules = {
            'link': v.stringType().notEmpty().length(max_value=512),
            'timeout': v.IntType().between(1, 600),
        }

        return cls.fv().validate(script_wget, rules)

    def get(self):
        item = {}
        for c in self.__table__.columns.keys():
            if c == 'id':
                continue
            item[c] = self._output_serialization(getattr(self, c))
        return item

    def get_config(self):
        item = {}
        for c in self.__table__.columns.keys():
            if c in ["id"]:
                continue
            item[c] = self._output_serialization(getattr(self, c))
        return item

    def update(self, data: Dict[str, Any]) -> 'ScriptWgetModel':
        self.link = data['link'] if 'link' in data.keys() else self.link
        self.timeout = data['timeout'] if 'timeout' in data.keys() else self.timeout
        return self
