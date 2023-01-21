from typing import Dict, Any

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.db import db, TimestampsModel, UuidModel
from respect_validation import Validator as v
from api.src.models import UserGroupMembers


class UserGroupModel(TimestampsModel, db.Model):
    __tablename__ = 'user_groups'

    name = db.Column(db.String(256), unique=True, nullable=False)
    permissions = relationship("UserGroupPermissions", backref="user_group_permissions", cascade="all, delete-orphan")
    users = relationship("UserModel", secondary=UserGroupMembers, viewonly=True)

    notification_config_links_user_groups = relationship("NotificationsConfigModel",
                                                         backref="notification_config_links_user_groups",
                                                         cascade="all,delete-orphan")

    relationships = ['permissions', 'users']
    not_sortable = ['permissions']

    additional_table_columns = ['permissions']

    references = [
        {
            "ref_model": UserGroupMembers,
            "ref_model_id": "user_group_id",
            "self_id": "id",
        }
    ]

    @classmethod
    def validate(cls, group, _id: str = None):
        rules = {
            'name': v.stringType().length(min_value=3, max_value=256).alnum('_-. ').noWhitespace().notExists(
                model=UserGroupModel, column="name", obj_id=_id),
            'permissions': v.listType().length(min_value=1).each(v.stringType()).containsAny(
                ['demo', 'admin', 'manager'])
        }

        return cls.fv().validate(group, rules)

    def get(self):
        item = {}
        for c in self.__table__.columns.keys():
            item[c] = self._output_serialization(getattr(self, c))
        permissions = []
        for permission in self.permissions:
            permissions.append(permission.permission)
        item["permissions"] = permissions
        return item

    def update(self, data: Dict[str, Any]) -> 'UserGroupModel':
        self.name = data['name'] if 'name' in data.keys() else self.name
        self.permissions = data['permissions'] if 'permissions' in data.keys() else self.permissions
        return self

    @classmethod
    def export(cls):
        export = []
        items = cls.query.all()

        for item in items:
            export.append({
                "id": str(item.id),
                "name": item.name,
                "permissions": [p.permission for p in item.permissions]
            })

        return export

    @classmethod
    def validate_import(cls, group: dict):
        _id = group.get('id', '')
        rules = {
            'name': v.stringType().length(min_value=3, max_value=256).alnum('_-. ').noWhitespace().notExists(
                model=cls, column="name", obj_id=_id),
            'permissions': v.listType().length(min_value=1).each(v.stringType())
        }
        if _id:
            rules['id'] = v.stringType().uuid().notExists(model=cls, column="id")

        return cls.fv().validate(group, rules)

    @classmethod
    def bulk_import(cls, groups: list):
        _error = False
        _validation = []
        _counter = 0
        for ug in groups:
            v = cls.validate_import(group=ug)
            if v.failed():
                _error = True
                _validation.append(v.get_messages())
            else:
                _permissions = ug['permissions']
                del ug['permissions']
                new_group = cls(**ug)
                new_group.save()

                permissions = []
                for permission in _permissions:
                    permissions.append(UserGroupPermissions(permission=permission, user_group_id=new_group.id))
                new_group.permissions = permissions
                new_group.save()
                _counter += 1
                _validation.append(None)

        return (_counter, _validation) if _error else (_counter, [])


class UserGroupPermissions(UuidModel, db.Model):
    __tablename__ = "user_group_permissions"

    user_group_id = db.Column(UUID(as_uuid=True), db.ForeignKey("user_groups.id"))
    permission = db.Column(db.String(80), nullable=False)
    # DO NOT UNCOMMENT BELOW! DO NOT TRY THIS S..T
    # user_group = relationship("UserGroupModel", foreign_keys='UserGroupPermissions.user_group_id', backref="user_groups")

    @staticmethod
    def bulk_insert(objects):
        db.session.add_all(objects)
        db.session.commit()
