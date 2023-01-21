from typing import Dict, Any
from sqlalchemy.orm import relationship

from api.db import db, TimestampsModel
from respect_validation import Validator as v


class RepositoryModel(TimestampsModel, db.Model):
    __tablename__ = 'repositories'

    name = db.Column(db.String(256), unique=True, nullable=False)
    description = db.Column(db.String(1024), nullable=False, unique=False, default='')
    icon = db.Column(db.String(1024), nullable=True, unique=False, default='')

    commits = db.Column(db.Integer(), default=None)
    size = db.Column(db.Integer(), default=None)
    last_commit = db.Column(db.TIMESTAMP, default=None)

    stats = relationship("RepoStatsModel", backref="repo_stats",
                         order_by='RepoStatsModel.date.asc()', cascade="all, delete-orphan")

    configs = relationship("ConfigModel", backref="repo_config", cascade="all, delete-orphan")
    configs_bin = relationship("ConfigBinModel", backref="repo_config_bin", cascade="all, delete-orphan")
    groups = relationship("RepoGroupModel", backref="repo_group", cascade="all, delete-orphan")

    notifications_links = relationship("NotificationsRepositoryModel", backref="repo_notifications_links",
                                       cascade="all,delete-orphan")

    # references = [
    #     {
    #         "model": ConfigModel,
    #         "reference": ConfigModel.repo_id
    #     }
    # ]

    @classmethod
    def find_by_name(cls, name: int) -> Any:  # here we use Any because it returns Any type
        return cls.query.filter_by(name=name).first()

    @classmethod
    def validate(cls, repo, _id: str = None, mode: str = 'add'):
        rules = {
            'name': v.stringType().length(min_value=3, max_value=256).alnum('_-. ').noWhitespace().notExists(
                model=RepositoryModel, column="name", obj_id=_id),
            'description': v.Optional(v.stringType().length(max_value=1024)),
            'icon': v.Optional(v.stringType().length(max_value=1024))
        }
        return cls.fv().validate(repo, rules)

    def get(self):
        item = {}
        for c in self.__table__.columns.keys():
            item[c] = self._output_serialization(getattr(self, c))
        stats = []
        for stat in self.stats:
            stats.append(stat.get())
        item["stats"] = stats
        return item

    def get_config(self):
        item = {}
        for c in self.__table__.columns.keys():
            if c in ["description", "icon", "groups"]:
                continue
            item[c] = self._output_serialization(getattr(self, c))
        item['configs'] = []
        for config in self.configs:
            item['configs'].append(config.get_config())
        return item

    def update(self, data: Dict[str, Any]) -> 'RepositoryModel':
        self.name = data['name'] if 'name' in data.keys() else self.name
        self.description = data['description'] if 'description' in data.keys() else self.description
        self.icon = data['icon'] if 'icon' in data.keys() else self.icon
        return self

    @classmethod
    def export(cls):
        export = []
        items = cls.query.all()

        for item in items:
            export.append({
                "id": str(item.id),
                "name": item.name,
                "description": item.description,
                "icon": item.icon
            })

        return export

    @classmethod
    def validate_import(cls, repo: dict):
        _id = repo.get('id', '')
        rules = {
            'name': v.stringType().length(min_value=3, max_value=256).alnum('_-. ').noWhitespace().notExists(
                model=RepositoryModel, column="name", obj_id=_id),
            'description': v.Optional(v.stringType().length(max_value=1024)),
            'icon': v.Optional(v.stringType().length(max_value=1024))
        }
        if _id:
            rules['id'] = v.stringType().uuid().notExists(model=cls, column="id")

        return cls.fv().validate(repo, rules)

    @classmethod
    def bulk_import(cls, repos: list):
        _error = False
        _validation = []
        _counter = 0
        for repo in repos:
            v = cls.validate_import(repo=repo)
            if v.failed():
                _error = True
                _validation.append(v.get_messages())
            else:
                _repo = cls(**repo)
                _repo.save()
                _counter += 1
                _validation.append(None)
        return (_counter, _validation) if _error else (_counter, [])
