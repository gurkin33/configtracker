import uuid
from datetime import datetime
from typing import Any, List

import sqlalchemy as sql
from flask_sqlalchemy import SQLAlchemy, Model
from respect_validation import FormValidator
from sqlalchemy.dialects.postgresql import UUID

convention = {
    "ix": "ix_%(column_0_lable)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


class ValidationModel(Model):

    @staticmethod
    def _output_serialization(data, date_format: str = "%Y-%m-%d %H:%M:%S"):
        if isinstance(data, str) or isinstance(data, int) or data is None:
            return data
        if isinstance(data, datetime):
            return data.strftime(date_format)
        if isinstance(data, uuid.UUID):
            return str(data)
        return str(data)

    @staticmethod
    def fv() -> 'FormValidator':
        return FormValidator()

    def save(self) -> None:
        if hasattr(self, "updated_at"):
            self.updated_at = sql.func.now()
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


ENGINE_OPTIONS = {
    "pool_size": 10,
    "max_overflow": 2,
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "pool_use_lifo": True
}
metadata = sql.MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata, model_class=ValidationModel, engine_options=ENGINE_OPTIONS)
# db.make_declarative_base(ValidationModel, metadata=metadata)


class TableModel(Model):
    __abstract__ = True
    __tablename__ = ''

    additional_table_columns = []
    not_sortable = []
    relationships = []
    references = []

    @classmethod
    def get_ref_count(cls, item_id: str):
        query = cls.query
        for r in cls.references:
            if type(r['ref_model']) == sql.Table:
                query = query.join(
                    r["ref_model"],
                    getattr(r["ref_model"].c, r["ref_model_id"]) == getattr(cls, r["self_id"]),
                    isouter=True
                ).filter(getattr(r["ref_model"].c, r["ref_model_id"]).isnot(None))
            else:
                query = query.join(
                    r["ref_model"],
                    getattr(r["ref_model"], r["ref_model_id"]) == getattr(cls, r["self_id"]),
                    isouter=True
                ).filter(getattr(r["ref_model"], r["ref_model_id"]).isnot(None))
        return query.filter(cls.id == item_id).count()


class UuidModel(TableModel):

    id = sql.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)

    @classmethod
    def find_by_id(cls, _id: str) -> Any:  # here we use Any because it returns Any type
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_all_id(cls, _ids: List[str]) -> Any:  # here we use Any because it returns Any type
        return db.session.query(cls).filter(cls.id.in_(_ids)).all()


class TimestampsModel(UuidModel):
    created_at = sql.Column(sql.TIMESTAMP, server_default=sql.func.now())
    updated_at = sql.Column(
                sql.TIMESTAMP, server_default=sql.func.now())

    # @declared_attr
    # def create_at_str(self):
    #     return column_property(func.to_char(self.created_at, 'YYYY-MM-DD HH24:MI:SS'))

    # @declared_attr
    # def updated_at_str(self):
    #     return column_property(func.to_char(self.updated_at, 'YYYY-MM-DD HH24:MI:SS'))
