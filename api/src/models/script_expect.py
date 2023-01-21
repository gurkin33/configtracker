from typing import Dict, Any
from sqlalchemy.orm import relationship

from api.db import db, UuidModel
from respect_validation import Validator as v


class ScriptExpectModel(UuidModel, db.Model):
    __tablename__ = 'scripts_expect'

    protocol = db.Column(db.String(128), nullable=False, default="ssh")
    port = db.Column(db.Integer(), nullable=False, default=22)
    username_prompt = db.Column(db.String(256), nullable=False, default="sername:, ogin:")
    password_prompt = db.Column(db.String(256), nullable=False, default="assword:")
    default_prompt = db.Column(db.String(256), nullable=False, default=">, #")
    timeout = db.Column(db.Integer(), nullable=False, default=10)
    expectations = relationship("ExpectationModel", backref="script_expectations",
                                order_by='ExpectationModel.order.asc()', cascade="all,delete-orphan")
                                #, cascade="all, delete-orphan")

    relationships = ['expectations']

    @classmethod
    def validate(cls, script_expect, _id: str = ''):
        rules = {
            'protocol': v.stringType().notEmpty().include(['ssh', 'telnet']),
            'port': v.IntType().notEmpty().between(1, 64000),
            'username_prompt': v.stringType().notEmpty().length(max_value=256).set_name('Username prompt'),
            'password_prompt': v.stringType().notEmpty().length(max_value=256).set_name('Password prompt'),
            'default_prompt': v.stringType().notEmpty().length(max_value=256).set_name('Default prompt'),
            'timeout': v.IntType().between(1, 300),
            'expectations': v.listType().notEmpty().each(v.keySet(
                                v.key('prompt', v.stringType().length(max_value=256)),
                                v.key('cmd', v.stringType().notEmpty().length(max_value=1024).set_name('Command')),
                                v.key('timeout', v.intType().between(0, 600)),
                                v.key('order', v.intType().between(0, 300)),
                                v.key('save', v.boolType()),
                                v.key('secret', v.boolType()),
                                v.key('skip_top', v.intType().between(0, 600)),
                                v.key('skip_bottom', v.intType().between(0, 600)),
                            ).set_name('Expectations'))
        }

        return cls.fv().validate(script_expect, rules)

    def get(self):
        item = {}
        for c in self.__table__.columns.keys():
            if c in ['id']:
                continue
            item[c] = self._output_serialization(getattr(self, c))
        expectations = []
        for expectation in self.expectations:
            expectations.append(expectation.get())
        item["expectations"] = expectations
        return item

    def get_config(self):
        item = {}
        for c in self.__table__.columns.keys():
            if c in ["id"]:
                continue
            if c in ["username_prompt", "password_prompt", "default_prompt"]:
                item[c] = self._output_serialization(getattr(self, c)).split(",")
                continue
            item[c] = self._output_serialization(getattr(self, c))
        expectations = []
        for expectation in self.expectations:
            expectations.append(expectation.get_config())
        item["expectations"] = expectations
        return item

    def get_export(self):
        item = {}
        for c in self.__table__.columns.keys():
            if c in ["id"]:
                continue
            item[c] = self._output_serialization(getattr(self, c))
        expectations = []
        for expectation in self.expectations:
            expectations.append(expectation.get())
        item["expectations"] = expectations
        return item

    def update(self, data: Dict[str, Any]) -> 'ScriptExpectModel':
        self.protocol = data['protocol'] if 'protocol' in data.keys() else self.protocol
        self.port = data['port'] if 'port' in data.keys() else self.port
        self.username_prompt = data['username_prompt'] if 'username_prompt' in data.keys() else self.username_prompt
        self.password_prompt = data['password_prompt'] if 'password_prompt' in data.keys() else self.password_prompt
        self.default_prompt = data['default_prompt'] if 'default_prompt' in data.keys() else self.default_prompt
        self.timeout = data['timeout'] if 'timeout' in data.keys() else self.timeout
        self.expectations = data['expectations'] if 'expectations' in data.keys() else self.expectations
        return self
