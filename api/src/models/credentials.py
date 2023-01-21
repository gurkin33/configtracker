from typing import Dict, Any

from api.src.encryptor import Encryptor
from api.src.models.config import ConfigModel

from api.db import db, TimestampsModel
from respect_validation import Validator as v


class CredentialsModel(TimestampsModel, db.Model):
    __tablename__ = 'credentials'

    name = db.Column(db.String(256), unique=True, nullable=False)
    username = db.Column(db.String(256), unique=False, nullable=False, default="")
    password = db.Column(db.String(2048), unique=False, nullable=False, default="")
    ssh_key = db.Column(db.String(4096), unique=False, nullable=False, default="")
    # type values: user-creds, password, ssh-key
    type = db.Column(db.String(32), unique=False, nullable=False, default="user-creds")

    references = [
        {
            "ref_model": ConfigModel,
            "ref_model_id": "credentials_id",
            "self_id": "id",
        }
    ]

    @classmethod
    def validate(cls, credentials: dict, _id: str = None):
        rules = {
            'name': v.stringType().length(min_value=3, max_value=256).alnum('_-.').noWhitespace().notExists(
                model=CredentialsModel, column="name", obj_id=_id),
            'username': v.stringType().notEmpty().length(max_value=256),
            'password': v.stringType().notEmpty().length(max_value=256),
            'ssh_key': v.stringType().notEmpty().length(max_value=4096).set_name('SSH Key'),
            'type': v.stringType().notEmpty().include(['user-creds', 'password', 'ssh-key']).length(max_value=32),
        }

        if not _id == '':
            rules['password'] = v.Optional(rules['password'])
            rules['ssh_key'] = v.Optional(rules['ssh_key'])

        if credentials.get('type', None) and credentials['type'] == 'password':
            rules['username'] = v.Optional(rules['username'])

        if credentials.get('type', None) and credentials['type'] == 'ssh-key':
            rules['password'] = v.Optional(rules['password'])
            # rules['ssh_key'] = v.Optional(rules['ssh_key'])
        else:
            rules['ssh_key'] = v.Optional(rules['ssh_key'])

        return cls.fv().validate(credentials, rules)

    def get(self):
        item = {}
        for c in self.__table__.columns.keys():
            item[c] = self._output_serialization(getattr(self, c))
        return item

    def get_config(self):
        item = {}
        for c in self.__table__.columns.keys():
            if c in ["id", "created_at", "updated_at", "name"]:
                continue
            item[c] = self._output_serialization(getattr(self, c))
        return item

    def update(self, data: Dict[str, Any]) -> 'CredentialsModel':
        self.name = data['name'] if 'name' in data.keys() else self.name
        self.username = data['username'] if 'username' in data.keys() else self.username
        self.password = Encryptor.run(data['password']) if 'password' in data.keys() else self.password
        self.ssh_key = Encryptor.run(data['ssh_key']) if 'ssh_key' in data.keys() else self.ssh_key
        self.type = data['type'] if 'type' in data.keys() else self.type
        return self

    @classmethod
    def export(cls):
        export = []
        items = cls.query.all()

        for item in items:
            export.append({
                "id": str(item.id),
                "name": item.name,
                "username": item.username,
                "password": item.password,
                "ssh_key": item.ssh_key,
                "type": item.type
            })

        return export

    @classmethod
    def validate_import(cls, creds: dict):
        _id = creds.get('id', '')
        rules = {
            'name': v.stringType().length(min_value=3, max_value=256).alnum('_-.').noWhitespace().notExists(
                model=CredentialsModel, column="name", obj_id=_id),
            'username': v.stringType().notEmpty().length(max_value=256),
            'password': v.stringType().notEmpty().length(max_value=256),
            'ssh_key': v.stringType().notEmpty().length(max_value=4096).set_name('SSH Key'),
            'type': v.stringType().notEmpty().include(['user-creds', 'password', 'ssh-key']).length(max_value=32),
        }

        if not _id == '':
            rules['password'] = v.Optional(rules['password'])
            rules['ssh_key'] = v.Optional(rules['ssh_key'])

        if creds.get('type', None) and creds['type'] == 'password':
            rules['username'] = v.Optional(rules['username'])

        if creds.get('type', None) and creds['type'] == 'ssh-key':
            rules['password'] = v.Optional(rules['password'])
            # rules['ssh_key'] = v.Optional(rules['ssh_key'])
        else:
            rules['ssh_key'] = v.Optional(rules['ssh_key'])
        if _id:
            rules['id'] = v.stringType().uuid().notExists(model=cls, column="id")

        return cls.fv().validate(creds, rules)

    @classmethod
    def bulk_import(cls, credentials: list):
        _error = False
        _validation = []
        _counter = 0
        for creds in credentials:
            v = cls.validate_import(creds=creds)
            if v.failed():
                _error = True
                _validation.append(v.get_messages())
            else:
                _creds = cls(**creds)
                _creds.save()
                _counter += 1
                _validation.append(None)
        return (_counter, _validation) if _error else (_counter, [])
