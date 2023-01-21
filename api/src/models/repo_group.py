import uuid
from typing import Dict, Any

from sqlalchemy import literal, cast, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, aliased

from api.db import db, TimestampsModel
from respect_validation import Validator as v


class RepoGroupModel(TimestampsModel, db.Model):
    __tablename__ = 'repo_groups'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(256), nullable=False)
    description = db.Column(db.String(1024), nullable=False, unique=False, default='')
    configs = relationship("ConfigModel", backref="repo_group_config", viewonly=True)
    repo_id = db.Column(UUID(as_uuid=True), db.ForeignKey('repositories.id'))
    parent_id = db.Column(UUID(as_uuid=True), db.ForeignKey('repo_groups.id'))
    parent = relationship("RepoGroupModel", remote_side=[id], backref="parent_groups",
                          lazy="joined", join_depth=1, viewonly=True)
    # tree variables
    fullpath = db.Column(db.Text(), nullable=False, default='/')
    fullpath_id = db.Column(db.Text(), nullable=False, default='/')
    level = db.Column(db.Integer(), unique=False, nullable=False, default=0)
    expandable = db.Column(db.Boolean(), nullable=False, default=False)
    # children = relationship("RepoGroupModel", lazy="joined", join_depth=1)

    notifications_links = relationship("NotificationsRepoGroupModel", backref="repo_group_notifications_links",
                                       cascade="all,delete-orphan")

    @classmethod
    def find_by_name(cls, name: int) -> Any:  # here we use Any because it returns Any type
        return cls.query.filter_by(name=name).first()

    @classmethod
    def validate(cls, repo_group, _id: str = '', repo_id: str = ''):
        rules = {
            'name': v.stringType().length(min_value=3, max_value=256).alnum('_-. ').noWhitespace().RepoGroupNotExists(
                repo_id=repo_id, obj_id=_id, parent_id=repo_group.get('parent', None)),
            'description': v.Optional(v.stringType().length(max_value=1024)),
            'parent': v.oneOf(v.noneType(), v.stringType().CheckRepoGroupParent(_id).length(max_value=36))
            # 'parent': v.Optional(v.stringType().CheckRepoGroupParent(_id).length(max_value=36))
        }
        return cls.fv().validate(repo_group, rules)

    def get_without_parent(self):
        item = {}
        for c in self.__table__.columns.keys():
            if c in ['parent_id', 'repo_id']:
                continue
            item[c] = self._output_serialization(getattr(self, c))
        return item

    def get(self, parent_id: bool = False, repo_id: bool = False):
        item = {}
        for c in self.__table__.columns.keys():
            # if c in ['repo_id']:
            #     continue
            item[c] = self._output_serialization(getattr(self, c))

        if not repo_id:  # required for group tree
            del item['repo_id']
        if not parent_id:  # required for group tree
            del item['parent_id']
            item['parent'] = None
            # item['children'] = []
            if self.parent:
                item['parent'] = self.parent.get_without_parent()

        return item

    def update(self, data: Dict[str, Any] = {}) -> 'RepoGroupModel':
        self.name = data['name'] if 'name' in data.keys() else self.name
        self.description = data['description'] if 'description' in data.keys() else self.description
        # self.parent_id = data['parent_id'] if 'parent_id' in data.keys() else self.parent_id
        self.parent_id = data['parent']
        if self.parent_id:
            row = RepoGroupModel.repo_group_tree_model(repo_id=self.repo_id).filter(
                RepoGroupModel.id == self.parent_id).one()
            self.fullpath = f'{row[2]}/{self.name}'
            self.fullpath_id = f'{row[3]}/{self.id}'
            self.level = row[1] + 1
            RepoGroupModel.query.filter_by(id=self.parent_id).update(dict(expandable=True))
        else:
            self.fullpath = f'/{self.name}'
            self.fullpath_id = f'/{self.id}'
            self.level = 0

        self.expandable = bool(RepoGroupModel.query.filter(RepoGroupModel.parent_id == self.id).count())

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
                "repo_id": str(item.repo_id),
                "parent_id": str(item.parent_id) if item.parent_id else None
            })

        return export

    @classmethod
    def validate_import(cls, repo_group: dict):
        _id = repo_group.get('id', None)
        _repo_id = repo_group.get('repo_id', None)
        rules = {
            'name': v.stringType().length(min_value=3, max_value=256).alnum('_-. ').noWhitespace().RepoGroupNotExists(
                repo_id=_repo_id, obj_id=_id, parent_id=repo_group.get('parent', None)),
            'description': v.Optional(v.stringType().length(max_value=1024)),
            'parent_id': v.oneOf(v.noneType(), v.stringType().CheckRepoGroupParent(_id).length(max_value=36)),
            'repo_id': v.stringType().uuid().repo_exists()
        }
        if _id:
            rules['id'] = v.stringType().uuid().notExists(model=cls, column="id")

        return cls.fv().validate(repo_group, rules)

    @classmethod
    def bulk_import(cls, repo_groups: list):
        _error = False
        _validation = []
        _counter = 0
        for repo_group in repo_groups:
            v = cls.validate_import(repo_group=repo_group)
            if v.failed():
                _error = True
                _validation.append(v.get_messages())
            else:
                _repo_group = cls(**repo_group)
                _repo_group.save()
                _counter += 1
                _validation.append(None)
        return (_counter, _validation) if _error else (_counter, [])

    @classmethod
    def repo_group_tree_model(cls, repo_id: str = '', order: bool = True):
        hierarchy = db.session.query(
            cls,
            literal(0).label("level_"),
            cast(func.concat("/", cls.name), db.String(2000)).label("fullpath_"),
            cast(func.concat("/", cls.id), db.String(4000)).label("fullpath_id_"),
        )
        if repo_id:
            hierarchy = hierarchy.filter(
                cls.repo_id == repo_id,
                cls.parent_id == None,
            ).cte('hierarchy', recursive=True)
        else:
            hierarchy = hierarchy.filter(
                cls.parent_id == None,
            ).cte('hierarchy', recursive=True)

        parent = aliased(hierarchy, 'p')
        children = aliased(cls, name="c")
        hierarchy = hierarchy.union_all(
            db.session.query(
                children,
                (parent.c.level_ + 1).label("level_"),
                cast(func.concat(parent.c.fullpath, "/", children.name), db.String(2000)).label("fullpath_"),
                cast(func.concat(parent.c.fullpath_id, "/", children.id), db.String(4000)).label("fullpath_id_"),
            ).filter(children.parent_id == parent.c.id))
        if order:
            return db.session.query(cls, hierarchy.c.level_, hierarchy.c.fullpath_, hierarchy.c.fullpath_id_)\
                .select_entity_from(hierarchy).order_by(hierarchy.c.level_).order_by(hierarchy.c.name)
        else:
            return db.session.query(cls, hierarchy.c.level_, hierarchy.c.fullpath_, hierarchy.c.fullpath_id_) \
                .select_entity_from(hierarchy)
