from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.db import db, UuidModel
from respect_validation import Validator as v

from api.src.models.user import UserModel
from api.src.models.user_group import UserGroupModel


class NotificationParent:

    @classmethod
    def validate(cls, data, config: bool = True):
        rules = {
            'user_ids': v.listType().each(v.exists_in_db(model=UserModel)),
            'group_ids': v.listType().each(v.exists_in_db(model=UserGroupModel))
        }

        if config:
            rules["other_emails"] = v.listType().each(v.email()).set_name("Other emails")
            if len(','.join(data["other_emails"])) > 2048:
                data["other_emails"] = ','.join(data["other_emails"])
                rules["other_emails"] = v.stringType().length(max_value=2048).set_name("Other emails")

        return cls.fv().validate(data, rules)

    @classmethod
    def insert(cls, data, _id: dict):
        cls.query.filter_by(**_id).delete()
        if data:
            db.session.add_all(data)
        db.session.commit()

    @classmethod
    def insert_children(cls, data):
        db.session.add_all(data)
        db.session.commit()

    @classmethod
    def get(cls, _id: dict):
        output = {
            "users": [],
            "groups": []
        }
        notifications = cls.query.filter_by(**_id).all()
        for n in notifications:
            if n.user_id:
                output['users'].append(n.users.get())
            if n.group_id:
                output['groups'].append(n.groups.get())
        return output


class NotificationsConfigModel(UuidModel, db.Model, NotificationParent):
    __tablename__ = 'notifications_config'

    config_id = db.Column(UUID(as_uuid=True), db.ForeignKey("configs.id"), nullable=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=True)
    group_id = db.Column(UUID(as_uuid=True), db.ForeignKey("user_groups.id"), nullable=True)

    users = relationship("UserModel", backref="notifications_config_2_user_link", viewonly=True)
    groups = relationship("UserGroupModel", backref="notifications_config_user_group_link", viewonly=True)

    @classmethod
    def get_emails(cls, config_id: str):
        emails = []
        users_notify = cls.query.with_entities(
            cls, UserModel
        ).outerjoin(UserModel).filter(
            cls.config_id == config_id,
            cls.user_id.is_not(None),
            cls.group_id.is_(None),
        ).all()
        for n, u, in users_notify:
            if u.email:
                emails.append(u.email)

        user_groups_notify = cls.query.with_entities(
            cls, UserGroupModel
        ).outerjoin(UserGroupModel).filter(
            cls.config_id == config_id,
            cls.user_id.is_(None),
            cls.group_id.is_not(None),
        ).all()
        for n, ug, in user_groups_notify:
            users = ug.users
            if users:
                for u in users:
                    if u.email:
                        emails.append(u.email)
        return list(set(emails))

    @classmethod
    def clear(cls, config_id: str):
        cls.query.filter(cls.config_id == config_id).delete()
        db.session.commit()

    @classmethod
    def inherit(cls, config_id: str, from_repo_id: str = '', from_group_id: str = ''):
        if not from_group_id and not from_repo_id:
            return
        if from_group_id:
            notifications = NotificationsRepoGroupModel.get_related(from_group_id)
        else:
            notifications = NotificationsRepositoryModel.get_related(from_repo_id)

        if notifications:
            cnu = []
            cng = []
            for n in notifications:
                if n.user_id:
                    cnu.append(NotificationsConfigModel(**{"config_id": config_id, "user_id": n.user_id}))
                if n.group_id:
                    cng.append(NotificationsConfigModel(**{"config_id": config_id, "group_id": n.group_id}))
            if cnu or cng:
                NotificationsConfigModel.insert([*cnu, *cng], {"config_id": config_id})

    @classmethod
    def export(cls):
        export = []
        items = cls.query.all()

        for item in items:
            export.append({
                "config_id": str(item.config_id),
                "user_id": str(item.user_id) if item.user_id else None,
                "group_id": str(item.group_id) if item.group_id else None,
            })

        return export

    @classmethod
    def validate_import(cls, notifications: dict):
        _config_id = notifications.get('config_id', None)

        rules = {
            'config_id': v.stringType().uuid().ConfigExists().set_name('Config ID'),
            'user_id': v.stringType().uuid().ExistsInDb(UserModel).NotificationsConfig(
                _config_id).set_name('User ID'),
            'group_id': v.stringType().uuid().ExistsInDb(UserGroupModel).NotificationsConfig(
                _config_id, user_id=False).set_name('User group ID'),
        }

        if notifications.get('user_id', None):
            rules['group_id'] = v.noneType()
        else:
            rules['user_id'] = v.noneType()

        return cls.fv().validate(notifications, rules)

    @classmethod
    def bulk_import(cls, notifications: list):
        _error = False
        _validation = []
        _counter = 0
        for n in notifications:
            v = cls.validate_import(notifications=n)
            if v.failed():
                _error = True
                _validation.append(v.get_messages())
            else:
                _config = cls(**n)
                _config.save()
                _counter += 1
                _validation.append(None)
        return (_counter, _validation) if _error else (_counter, [])


class NotificationsRepoGroupModel(UuidModel, db.Model, NotificationParent):
    __tablename__ = 'notifications_repo_group'

    repo_group_id = db.Column(UUID(as_uuid=True), db.ForeignKey("repo_groups.id"), nullable=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=True)
    group_id = db.Column(UUID(as_uuid=True), db.ForeignKey("user_groups.id"), nullable=True)

    users = relationship("UserModel", backref="notifications_repo_group_2_user_link", viewonly=True)
    groups = relationship("UserGroupModel", backref="notifications_repo_group_2_user_group_link", viewonly=True)

    @classmethod
    def get_related(cls, group_id: str):
        return cls.query.filter(cls.repo_group_id == group_id).all()

    @classmethod
    def clear(cls, group_id: str):
        cls.query.filter(cls.repo_group_id == group_id).delete()
        db.session.commit()

    @classmethod
    def inherit(cls, group_id: str, from_repo_id: str = '', from_group_id: str = ''):
        if not from_group_id and not from_repo_id:
            return
        if from_group_id:
            notifications = NotificationsRepoGroupModel.get_related(from_group_id)
        else:
            notifications = NotificationsRepositoryModel.get_related(from_repo_id)

        if notifications:
            cnu = []
            cng = []
            for n in notifications:
                if n.user_id:
                    cnu.append(NotificationsRepoGroupModel(**{"repo_group_id": group_id, "user_id": n.user_id}))
                if n.group_id:
                    cng.append(NotificationsRepoGroupModel(**{"repo_group_id": group_id, "group_id": n.group_id}))
            if cnu or cng:
                NotificationsRepoGroupModel.insert([*cnu, *cng], {"repo_group_id": group_id})

    @classmethod
    def export(cls):
        export = []
        items = cls.query.all()

        for item in items:
            export.append({
                "repo_group_id": str(item.repo_group_id),
                "user_id": str(item.user_id) if item.user_id else None,
                "group_id": str(item.group_id) if item.group_id else None,
            })

        return export

    @classmethod
    def validate_import(cls, notifications: dict):
        _repo_group_id = notifications.get('repo_group_id', None)

        rules = {
            'repo_group_id': v.stringType().uuid().RepoGroupExists().set_name('Repository group ID'),
            'user_id': v.stringType().uuid().ExistsInDb(UserModel).NotificationsRepoGroup(
                _repo_group_id).set_name('User ID'),
            'group_id': v.stringType().uuid().ExistsInDb(UserGroupModel).NotificationsRepoGroup(
                _repo_group_id, user_id=False).set_name('User group ID'),
        }

        if notifications.get('user_id', None):
            rules['group_id'] = v.noneType()
        else:
            rules['user_id'] = v.noneType()

        return cls.fv().validate(notifications, rules)

    @classmethod
    def bulk_import(cls, notifications: list):
        _error = False
        _validation = []
        _counter = 0
        for n in notifications:
            v = cls.validate_import(notifications=n)
            if v.failed():
                _error = True
                _validation.append(v.get_messages())
            else:
                _config = cls(**n)
                _config.save()
                _counter += 1
                _validation.append(None)
        return (_counter, _validation) if _error else (_counter, [])


class NotificationsRepositoryModel(UuidModel, db.Model, NotificationParent):
    __tablename__ = 'notifications_repo'

    repo_id = db.Column(UUID(as_uuid=True), db.ForeignKey("repositories.id"), nullable=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=True)
    group_id = db.Column(UUID(as_uuid=True), db.ForeignKey("user_groups.id"), nullable=True)

    users = relationship("UserModel", backref="notifications_repo_2_user_link", viewonly=True)
    groups = relationship("UserGroupModel", backref="notifications_repo_2_user_group_link", viewonly=True)

    @classmethod
    def get_related(cls, repo_id: str):
        return cls.query.filter(cls.repo_id == repo_id).all()

    @classmethod
    def export(cls):
        export = []
        items = cls.query.all()

        for item in items:
            export.append({
                "repo_id": str(item.repo_id),
                "user_id": str(item.user_id) if item.user_id else None,
                "group_id": str(item.group_id) if item.group_id else None,
            })

        return export

    @classmethod
    def validate_import(cls, notifications: dict):
        _repo_id = notifications.get('repo_id', None)

        rules = {
            'repo_id': v.stringType().uuid().repo_exists().set_name('Repository ID'),
            'user_id': v.stringType().uuid().ExistsInDb(UserModel).NotificationsRepo(_repo_id).set_name('User ID'),
            'group_id': v.stringType().uuid().ExistsInDb(UserGroupModel).NotificationsRepo(
                _repo_id, user_id=False).set_name('User group ID'),
        }

        if notifications.get('user_id', None):
            rules['group_id'] = v.noneType()
        else:
            rules['user_id'] = v.noneType()

        return cls.fv().validate(notifications, rules)

    @classmethod
    def bulk_import(cls, notifications: list):
        _error = False
        _validation = []
        _counter = 0
        for n in notifications:
            v = cls.validate_import(notifications=n)
            if v.failed():
                _error = True
                _validation.append(v.get_messages())
            else:
                _config = cls(**n)
                _config.save()
                _counter += 1
                _validation.append(None)
        return (_counter, _validation) if _error else (_counter, [])
