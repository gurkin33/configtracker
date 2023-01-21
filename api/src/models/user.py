import bcrypt
from typing import Dict, Any

from sqlalchemy.orm import relationship

from api.db import db, TimestampsModel
from respect_validation import Validator as v
from api.src.models import UserGroupMembers
from api.src.models.user_group import UserGroupModel


class UserModel(TimestampsModel, db.Model):
    __tablename__ = 'users'

    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(128), nullable=False, default='', server_default='')
    password = db.Column(db.String(512), unique=False, nullable=False)
    change_password = db.Column(db.Boolean(), nullable=False, default=False)
    firstname = db.Column(db.String(64), nullable=False, unique=False, server_default='', default='')
    lastname = db.Column(db.String(64), nullable=False, unique=False, server_default='', default='')
    pic = db.Column(db.String(512), nullable=True, unique=False, default='')
    language = db.Column(db.String(128), nullable=False, unique=False, server_default='en_EN')
    timezone = db.Column(db.String(32), nullable=False, unique=False, server_default='GMT-0')
    groups = relationship("UserGroupModel", secondary=UserGroupMembers, backref="UserModel")

    notification_config_links_users = relationship("NotificationsConfigModel",
                                                   backref="notification_config_links_users",
                                                   cascade="all,delete-orphan")

    # @classmethod
    # def find_by_id(cls, user_id: int) -> Any:  # here we use Any because it returns Any type
    #     return cls.query.filter_by(id=user_id).first()

    @classmethod
    def find_by_username(cls, username: int) -> Any:  # here we use Any because it returns Any type
        return cls.query.filter_by(username=username).first()

    @classmethod
    def validate(cls, user, _id: str = None, mode: str = 'add'):
        rules = {
            'username': v.stringType().length(min_value=3, max_value=80).alnum('_-.').noWhitespace().notExists(
                model=UserModel, column="username", obj_id=_id),
            'email': v.Optional(v.email()),
            'password': v.stringType().length(min_value=8, max_value=64),
            'change_password': v.Optional(v.boolType()),
            'firstname': v.Optional(v.stringType().length(min_value=2, max_value=64)),
            'lastname': v.Optional(v.stringType().length(min_value=2, max_value=64)),
            'pic': v.Optional(v.stringType()),
            'language': v.Optional(v.stringType()),
            'timezone': v.Optional(v.stringType()),
            'groups': v.list_type().each(v.userGroupExists())
        }

        # edit profile without rules below
        if _id and not user.get('username', None):
            del rules['username']
            del rules['groups']
        if mode == 'edit':
            rules['password'] = v.Optional(v.stringType().length(min_value=8, max_value=64))

        return cls.fv().validate(user, rules)

    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password.encode())

    def get(self, permissions: bool = False):
        item = {}
        for c in self.__table__.columns.keys():
            item[c] = self._output_serialization(getattr(self, c))
        groups = []
        for group in self.groups:
            groups.append({"name": group.name, "id": str(group.id)})
        item["groups"] = groups
        if permissions:
            item["permissions"] = []
            for g in self.groups:
                item["permissions"].extend(g.get()["permissions"])
            item["permissions"] = list(set(item["permissions"]))

        del item["password"]
        return item

    def update(self, data: Dict[str, Any]) -> 'UserModel':
        self.username = data['username'] if 'username' in data.keys() else self.username
        self.email = data['email'] if 'email' in data.keys() else self.email
        self.password = data['password'] if 'password' in data.keys() else self.password
        self.change_password = data['change_password'] if 'change_password' in data.keys() else self.change_password
        self.firstname = data['firstname'] if 'firstname' in data.keys() else self.firstname
        self.lastname = data['lastname'] if 'lastname' in data.keys() else self.lastname
        self.pic = data['pic'] if 'pic' in data.keys() else self.pic
        self.language = data['language'] if 'language' in data.keys() else self.language
        self.timezone = data['timezone'] if 'timezone' in data.keys() else self.timezone
        self.groups = data['groups'] if 'groups' in data.keys() else self.groups
        return self

    @classmethod
    def export(cls):
        export = []
        items = cls.query.all()

        for item in items:
            export.append({
                "id": str(item.id),
                "username": item.username,
                "password": item.password,
                "email": item.email,
                "firstname": item.firstname,
                "lastname": item.lastname,
                "pic": item.pic,
                "language": item.language,
                "timezone": item.timezone,
                "groups": [str(g.get()['id']) for g in item.groups]
            })

        return export

    @classmethod
    def validate_import(cls, user: dict):
        _id = user.get('id', '')
        rules = {
            'username': v.stringType().length(min_value=3, max_value=80).alnum('_-.').noWhitespace().notExists(
                model=UserModel, column="username", obj_id=_id),
            'email': v.Optional(v.email()),
            'password': v.stringType().length(min_value=8, max_value=64),
            'firstname': v.Optional(v.stringType().length(min_value=2, max_value=64)),
            'lastname': v.Optional(v.stringType().length(min_value=2, max_value=64)),
            'pic': v.Optional(v.stringType()),
            'language': v.Optional(v.stringType()),
            'timezone': v.Optional(v.stringType()),
            'groups': v.list_type().each(v.userGroupExists())
        }
        if _id:
            rules['id'] = v.stringType().uuid().notExists(model=cls, column="id")

        return cls.fv().validate(user, rules)

    @classmethod
    def bulk_import(cls, users: list):
        _error = False
        _validation = []
        _counter = 0
        for u in users:
            v = cls.validate_import(user=u)
            if v.failed():
                _error = True
                _validation.append(v.get_messages())
            else:
                u['groups'] = UserGroupModel.find_all_id(list([x for x in u["groups"]]))

                if not u['password'].startswith('$2'):
                    u['password'] = UserModel.hash_password(u['password'])

                new_user = UserModel(**u)
                new_user.save()
                _counter += 1
                _validation.append(None)

        return (_counter, _validation) if _error else (_counter, [])
