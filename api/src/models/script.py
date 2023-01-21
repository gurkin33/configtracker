import re
from typing import Dict, Any

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.db import db, TimestampsModel
from respect_validation import Validator as v

from api.src.encryptor import Encryptor
from api.src.models.config import ConfigModel

from api.src.models.script_wget import ScriptWgetModel
from api.src.models.script_file_transfer import ScriptFileTransferModel
from api.src.models.script_expect import ScriptExpectModel
from api.src.models.expectation import ExpectationModel


class ScriptModel(TimestampsModel, db.Model):
    __tablename__ = 'scripts'

    name = db.Column(db.String(256), unique=True, nullable=False)
    # type - expectations, file_transfer, wget, manual
    type = db.Column(db.String(128), unique=False, nullable=False, default="expect")
    expect_id = db.Column(UUID(as_uuid=True), db.ForeignKey("scripts_expect.id"), default=None)
    expect = relationship("ScriptExpectModel", cascade="all,delete", backref="script_expect")
    file_transfer_id = db.Column(UUID(as_uuid=True), db.ForeignKey("scripts_file_transfer.id"), default=None)
    file_transfer = relationship("ScriptFileTransferModel", cascade="all,delete", backref="script_file_transfer")
    wget_id = db.Column(UUID(as_uuid=True), db.ForeignKey("scripts_wget.id"), default=None)
    wget = relationship("ScriptWgetModel", cascade="all,delete", backref="script_wget")

    relationships = ['wget', 'file_transfer', 'expect']
    not_sortable = ['wget', 'file_transfer', 'expect']

    references = [
        {
            "ref_model": ConfigModel,
            "ref_model_id": "script_id",
            "self_id": "id",
        }
    ]

    @classmethod
    def validate(cls, script, _id: str = None):
        rules = {
            'name': v.stringType().length(min_value=3, max_value=256).alnum('_-. ').noWhitespace().notExists(
                model=ScriptModel, column="name", obj_id=_id),
            'type': v.stringType().notEmpty().length(max_value=128),
            'wget': v.AlwaysValid(),
            'file_transfer': v.AlwaysValid(),
            'expect': v.AlwaysValid(),
        }

        return cls.fv().validate(script, rules)

    def get(self):
        item = {}
        for c in self.__table__.columns.keys():
            if c in ['wget_id', 'expect_id', 'file_transfer_id']:
                continue
            item[c] = self._output_serialization(getattr(self, c))
        item['expect'] = self.expect.get() if self.expect_id else None
        item['file_transfer'] = self.file_transfer.get() if self.file_transfer_id else None
        item['wget'] = self.wget.get() if self.wget_id else None

        return item

    def get_config(self):
        item = {}
        for c in self.__table__.columns.keys():
            if c in ["id", "created_at", "updated_at", 'wget_id', 'expect_id', 'file_transfer_id']:
                continue
            item[c] = self._output_serialization(getattr(self, c))

        item['expect'] = self.expect.get_config() if self.expect_id else None
        item['file_transfer'] = self.file_transfer.get_config() if self.file_transfer_id else None
        item['wget'] = self.wget.get_config() if self.wget_id else None
        return item

    def get_export(self):
        item = {}
        for c in self.__table__.columns.keys():
            if c in ["created_at", "updated_at", 'wget_id', 'expect_id', 'file_transfer_id']:
                continue
            item[c] = self._output_serialization(getattr(self, c))

        item['expect'] = self.expect.get_export() if self.expect_id else None
        item['file_transfer'] = self.file_transfer.get_config() if self.file_transfer_id else None
        item['wget'] = self.wget.get_config() if self.wget_id else None
        return item

    def update(self, data: Dict[str, Any]) -> 'ScriptModel':
        self.name = data['name'] if 'name' in data.keys() else self.name
        self.type = data['type'] if 'type' in data.keys() else self.type
        self.wget = data['wget'] if 'wget' in data.keys() else self.wget
        self.expect = data['expect'] if 'expect' in data.keys() else self.expect
        self.file_transfer = data['file_transfer'] if 'file_transfer' in data.keys() else self.file_transfer
        return self

    @classmethod
    def export(cls):
        export = []
        items = cls.query.all()

        for item in items:
            export.append(item.get_export())

        return export

    @classmethod
    def validate_import(cls, script: dict):
        _id = script.get('id', '')
        rules = {
            'name': v.stringType().length(min_value=3, max_value=256).alnum('_-. ').noWhitespace().notExists(
                model=ScriptModel, column="name", obj_id=_id),
            'type': v.stringType().notEmpty().length(max_value=128),
            'wget': v.AlwaysValid(),
            'file_transfer': v.AlwaysValid(),
            'expect': v.AlwaysValid(),
        }
        if _id:
            rules['id'] = v.stringType().uuid().notExists(model=cls, column="id")

        return cls.fv().validate(script, rules)

    @classmethod
    def bulk_import(cls, scripts: list):
        _error = False
        _validation = []
        _counter = 0
        for script in scripts:
            _error2 = False
            v = cls.validate_import(script=script)
            if v.failed():
                _error = True
                _error2 = True
                _validation.append(v.get_messages())

            if script.get('wget', None) is not None:
                v = ScriptWgetModel.validate(script_wget=script['wget'])
                if v.failed():
                    _error = True
                    _error2 = True
                    _validation.append(v.get_messages())
                else:
                    script['wget'] = ScriptWgetModel(**script['wget'])

            if script.get('file_transfer', None) is not None:
                v = ScriptFileTransferModel.validate(script_file_transfer=script['file_transfer'])
                if v.failed():
                    _error = True
                    _error2 = True
                    _validation.append(v.get_messages())
                else:
                    script['file_transfer'] = ScriptWgetModel(**script['file_transfer'])

            if script.get('expect', None) is not None:
                v = ScriptExpectModel.validate(script_expect=script['expect'])
                if v.failed():
                    _error = True
                    _error2 = True
                    _validation.append(v.get_messages())
                else:
                    _expectations = []
                    for ex in script['expect']['expectations']:
                        if 'id' in ex.keys():
                            del ex['id']
                        if 'script_id' in ex.keys():
                            del ex['script_id']
                        if ex['secret'] and not re.search(r'fernet\((.*?)\)', ex['cmd']):
                            ex['cmd'] = Encryptor.run(ex['cmd'])
                        _expectations.append(ExpectationModel(**ex))
                    script['expect']['expectations'] = _expectations
                    script['expect'] = ScriptExpectModel(**script['expect'])

            if not _error2:
                _script = cls(**script)
                _script.save()
                _counter += 1
                _validation.append(None)

        return (_counter, _validation) if _error else (_counter, [])
