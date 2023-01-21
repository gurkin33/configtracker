from typing import Dict, Any

from api.db import db, UuidModel
from respect_validation import Validator as v


class ScriptFileTransferModel(UuidModel, db.Model):
    __tablename__ = 'scripts_file_transfer'

    path = db.Column(db.String(512), nullable=False)
    protocol = db.Column(db.String(16), nullable=False, default="scp")
    port = db.Column(db.Integer(), nullable=False, default="22")
    timeout = db.Column(db.Integer(), nullable=False, default="60")
    ftp_secure = db.Column(db.Boolean(), nullable=False, default=False)

    @classmethod
    def validate(cls, script_file_transfer, _id: str = ''):
        rules = {
            'path': v.stringType().notEmpty().length(max_value=512),
            'protocol': v.stringType().notEmpty().include(['sftp', 'ftp']).length(max_value=16),
            'port': v.IntType().between(1, 64000),
            'timeout': v.IntType().between(1, 600),
            'ftp_secure': v.BoolType(),
        }

        return cls.fv().validate(script_file_transfer, rules)

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

    def update(self, data: Dict[str, Any]) -> 'ScriptFileTransferModel':
        self.port = data['port'] if 'port' in data.keys() else self.port
        self.protocol = data['protocol'] if 'protocol' in data.keys() else self.protocol
        self.timeout = data['timeout'] if 'timeout' in data.keys() else self.timeout
        self.ftp_secure = data['ftp_secure'] if 'ftp_secure' in data.keys() else self.ftp_secure
        return self
