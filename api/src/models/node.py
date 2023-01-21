from typing import Dict, Any

from api.db import db, TimestampsModel
from respect_validation import Validator as v
from api.src.models.config import ConfigModel


class NodeModel(TimestampsModel, db.Model):
    __tablename__ = 'nodes'

    name = db.Column(db.String(256), unique=True, nullable=False)
    address = db.Column(db.String(512), unique=True, nullable=False, default="")

    # relationships = []

    references = [
        {
            "ref_model": ConfigModel,
            "ref_model_id": "node_id",
            "self_id": "id",
        }
    ]

    @classmethod
    def validate(cls, node, _id: str = None):
        rules = {
            'name': v.stringType().length(min_value=3, max_value=256).alnum('_-. ').noWhitespace().notExists(
                model=NodeModel, column="name", obj_id=_id),
            'address': v.stringType().notEmpty().addressNotExists(_id).length(max_value=512),
        }

        return cls.fv().validate(node, rules)

    def get(self):
        item = {}
        for c in self.__table__.columns.keys():
            item[c] = self._output_serialization(getattr(self, c))
        return item

    def get_config(self):
        item = {}
        for c in self.__table__.columns.keys():
            if c in ["id", "created_at", "updated_at"]:
                continue
            item[c] = self._output_serialization(getattr(self, c))
        return item

    def update(self, data: Dict[str, Any]) -> 'NodeModel':
        self.name = data['name'] if 'name' in data.keys() else self.name
        self.address = data['address'] if 'address' in data.keys() else self.address
        return self

    @classmethod
    def export(cls):
        export = []
        items = cls.query.all()

        for item in items:
            export.append({
                "id": str(item.id),
                "name": item.name,
                "address": item.address
            })

        return export

    @classmethod
    def validate_import(cls, node: dict):
        _id = node.get('id', '')
        rules = {
            'name': v.stringType().length(min_value=3, max_value=256).alnum('_-. ').noWhitespace().notExists(
                model=NodeModel, column="name", obj_id=_id),
            'address': v.stringType().notEmpty().addressNotExists(_id).length(max_value=512),
        }
        if _id:
            rules['id'] = v.stringType().uuid().notExists(model=cls, column="id")

        return cls.fv().validate(node, rules)

    @classmethod
    def bulk_import(cls, nodes: list):
        _error = False
        _validation = []
        _counter = 0
        for node in nodes:
            v = cls.validate_import(node=node)
            if v.failed():
                _error = True
                _validation.append(v.get_messages())
            else:
                _node = cls(**node)
                _node.save()
                _counter += 1
                _validation.append(None)
        return (_counter, _validation) if _error else (_counter, [])
