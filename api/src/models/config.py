from typing import Dict, Any
from sqlalchemy import and_, case
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.config import GlobalConfig
from api.db import db, TimestampsModel
from respect_validation import Validator as v

from api.src.models.config_git_parent import ConfigGitParent
from api.src.models.repo_group import RepoGroupModel
from api.src.models.notifications import NotificationsConfigModel


class ConfigModel(ConfigGitParent, TimestampsModel, db.Model):
    __tablename__ = 'configs'

    name = db.Column(db.String(256), nullable=False)
    exists = db.Column(db.Boolean(), nullable=False, default=False)
    status = db.Column(db.Boolean(), nullable=True, default=None)
    in_process = db.Column(db.Boolean(), nullable=True, default=False)
    size = db.Column(db.Integer(), nullable=True, default=None)
    last_modification = db.Column(db.TIMESTAMP(), nullable=True, default=None)

    node_id = db.Column(UUID(as_uuid=True), db.ForeignKey("nodes.id"), nullable=False)
    node = relationship("NodeModel", backref="config_node", viewonly=True)

    credentials_id = db.Column(UUID(as_uuid=True), db.ForeignKey("credentials.id"), nullable=True)
    credentials = relationship("CredentialsModel", backref="config_credentials", viewonly=True)

    script_id = db.Column(UUID(as_uuid=True), db.ForeignKey("scripts.id"), nullable=False)
    script = relationship("ScriptModel", backref="config_script", viewonly=True)

    repo_id = db.Column(UUID(as_uuid=True), db.ForeignKey("repositories.id"), nullable=False)
    repo = relationship("RepositoryModel", backref="config_repo", viewonly=True)

    repo_group_id = db.Column(UUID(as_uuid=True), db.ForeignKey("repo_groups.id"), nullable=True)
    repo_group = relationship("RepoGroupModel", backref="config_repo_group", viewonly=True)

    reports = relationship("ConfigReportModel", backref="config_reports",
                                order_by='ConfigReportModel.created_at.desc()', cascade="all,delete-orphan")

    commit_notes = relationship("CommitNotesModel", backref="config_notes", cascade="all,delete")

    style = db.Column(db.String(1024), nullable=True, default="")
    icon = db.Column(db.String(1024), nullable=True, default="")

    notifications = db.Column(db.String(2048), nullable=False, default="")
    notifications_links = relationship("NotificationsConfigModel", backref="config_notifications_links",
                                       cascade="all,delete-orphan")

    relationships = ['node', 'script', 'credentials', 'repo_group', 'repo']
    additional_table_columns = ['node', 'script', 'credentials', 'repo_group', 'repo']

    @classmethod
    def validate(cls, config, _id: str = None, repo_id: str = None, _try: bool = False):

        repo_group_id = None
        if 'repo_group' in config.keys() and isinstance(config['repo_group'], dict):
            repo_group_id = config['repo_group'].get('id', None)

        creds_id = None
        if 'credentials' in config.keys() and config['credentials'] and config['credentials'].get('id', None):
            creds_id = config['credentials']['id']

        rules = {
            'name': v.stringType().length(min_value=3, max_value=256).alnum('_-. ').noWhitespace().ConfigNameNotExists(
                repo_id=repo_id, group_id=repo_group_id, _id=_id),
            'node': v.notEmpty().dictType().key(
                "id", v.stringType().notEmpty().NodeExists().set_name('Node')
            ),
            'script': v.notEmpty().dictType().key(
                "id", v.stringType().notEmpty().ScriptExists().Script2Credentials(creds_id).set_name('Script')
            ),

            'repo_group': v.Optional(v.dictType().key(
                "id", v.stringType().notEmpty().repoGroupExists(repo_id=repo_id)).set_name('Repository group')),

            'credentials': v.Optional(v.dictType().key(
                "id", v.stringType().notEmpty().CredentialsExists())),

            'style': v.stringType().length(max_value=512),
            'icon': v.stringType().length(max_value=512),
        }

        if _try:
            del rules['name']
            del rules['style']
            del rules['icon']
            del rules['repo_group']
            if 'name' in config.keys():
                del config['name']
            if 'style' in config.keys():
                del config['style']
            if 'icon' in config.keys():
                del config['icon']
            if 'repo_group' in config.keys():
                del config['repo_group']

        return cls.fv().validate(config, rules)

    def get(self, get_repo: bool = False):
        item = {}
        for c in self.__table__.columns.keys():
            if c in ['node_id', 'script_id', 'repo_id', 'repo_group_id', 'credentials_id']:
                continue
            item[c] = self._output_serialization(getattr(self, c))
        item['node'] = self.node.get()
        item['script'] = self.script.get()
        item['repo_group'] = None
        if self.repo_group_id:
            item['repo_group'] = self.repo_group.get()
        item['credentials'] = None
        if self.credentials_id:
            item['credentials'] = self.credentials.get()
        if get_repo:
            item['repo'] = self.repo.get()
        return item

    def get_config(self):
        item = {}
        for c in self.__table__.columns.keys():
            if c in ['node_id', 'script_id', 'repo_group_id', 'credentials_id']:
                continue
            item[c] = self._output_serialization(getattr(self, c))
        item['node'] = self.node.get_config()
        item['script'] = self.script.get_config()
        item['credentials'] = None
        if self.credentials_id:
            item['credentials'] = self.credentials.get_config()
        item['emails'] = NotificationsConfigModel.get_emails(self.id)
        if self.notifications:
            item['emails'] = list({*item['emails'], *self.notifications.split(', ')})
        return item

    def update(self, data: Dict[str, Any]) -> 'ConfigModel':
        self.name = data['name'] if 'name' in data.keys() else self.name
        self.style = data['style'] if 'style' in data.keys() else self.style
        self.icon = data['icon'] if 'icon' in data.keys() else self.icon
        self.script_id = data['script']['id'] if 'script' in data.keys() else self.script_id
        self.node_id = data['node']['id'] if 'node' in data.keys() else self.node_id

        if 'repo_group' in data.keys() and not data['repo_group']:
            self.repo_group_id = None
        elif 'repo_group' in data.keys():
            self.repo_group_id = data['repo_group']['id']
        if 'credentials' in data.keys() and not data['credentials']:
            self.credentials_id = None
        elif 'credentials' in data.keys():
            self.credentials_id = data['credentials']['id']
        return self

    @classmethod
    def config_tree_query(cls, repo_id: str = None, group_id: str = None):

        if repo_id and group_id == 'all':
            hierarchy = RepoGroupModel.repo_group_tree_model(repo_id=repo_id, order=False).subquery()
            return db.session.query(cls,
                                    hierarchy.c.level,
                                    hierarchy.c.fullpath).join(hierarchy,
                                                               and_(
                                                                   hierarchy.c.id == cls.repo_group_id,
                                                                   cls.repo_id == repo_id,
                                                               ),
                                                               isouter=True).filter(cls.repo_id == repo_id)

        if repo_id and group_id:
            hierarchy = RepoGroupModel.repo_group_tree_model(order=False).subquery()
            return db.session.query(cls,
                                    hierarchy.c.level,
                                    hierarchy.c.fullpath).join(hierarchy,
                                                               and_(
                                                                   hierarchy.c.id == cls.repo_group_id,
                                                                   cls.repo_id == repo_id,
                                                                   cls.repo_group_id == group_id
                                                               ),
                                                                isouter=True).filter(
                and_(cls.repo_id == repo_id, cls.repo_group_id == group_id))

        if repo_id and not group_id:
            hierarchy = RepoGroupModel.repo_group_tree_model(repo_id=repo_id, order=False).subquery()
            return db.session.query(cls,
                                    hierarchy.c.level,
                                    hierarchy.c.fullpath).join(hierarchy,
                                                               and_(
                                                                   hierarchy.c.id == cls.repo_group_id,
                                                                   cls.repo_id == repo_id,
                                                                   cls.repo_group_id == None
                                                               ),
                                                               isouter=True).filter(
                and_(cls.repo_id == repo_id, cls.repo_group_id == None))

    @classmethod
    def set_in_process(cls, config_id: str = None):
        if config_id is None:
            cls.query.update({cls.in_process: True})
            db.session.commit()
        else:
            db.session.query(cls).\
                filter(cls.id == config_id).update({cls.in_process: False})
            db.session.commit()

    @classmethod
    def set_config_properties(cls, properties: list):
        ids = [c[0] for c in properties]
        payload_size = [[c[0], c[1]] for c in properties]
        payload_mod_time = [[c[0], c[2]] for c in properties]
        db.session.query(cls).filter(cls.id.in_(ids))\
            .update({
                cls.size: case(
                    payload_size,
                    value=cls.id
                ),
                cls.last_modification: case(
                    payload_mod_time,
                    value=cls.id
                )
            })
        db.session.commit()

    def is_exists(self):
        return v.file().validate(f"{GlobalConfig.REPOS_ROOT_PATH}/{self.repo_id}/{self.id}")

    @classmethod
    def export(cls):
        export = []
        items = cls.query.all()

        for item in items:
            export.append({
                "id": str(item.id),
                "name": item.name,
                "node_id": str(item.node_id),
                "credentials_id": str(item.credentials_id) if item.credentials_id else None,
                "script_id": str(item.script_id),
                "repo_id": str(item.repo_id),
                "repo_group_id": str(item.repo_group_id) if item.repo_group_id else None,
                "style": item.style,
                "icon": item.icon,
                "notifications": item.notifications
            })

        return export

    @classmethod
    def validate_import(cls, config: dict):
        _id = config.get('id', '')
        _repo_id = config.get('repo_id', '')
        _repo_group_id = config.get('repo_group_id', None)

        rules = {
            'name': v.stringType().length(min_value=3, max_value=256).alnum('_-. ').noWhitespace().ConfigNameNotExists(
                repo_id=_repo_id, group_id=_repo_group_id, _id=_id),
            'node_id': v.stringType().notEmpty().NodeExists().set_name('Node ID'),
            'script_id':  v.stringType().notEmpty().ScriptExists().set_name('Script ID'),

            'repo_id': v.stringType().uuid().repo_exists().set_name('Repository ID'),

            'repo_group_id': v.Optional(v.stringType().notEmpty().repoGroupExists(
                repo_id=_repo_id).set_name('Repository group ID')),

            'credentials_id': v.Optional(v.stringType().notEmpty().CredentialsExists()),

            'style': v.stringType().length(max_value=512),
            'icon': v.stringType().length(max_value=512),
            'notifications': v.stringType().length(max_value=2048),
        }
        if _id:
            rules['id'] = v.stringType().uuid().notExists(model=cls, column="id")

        return cls.fv().validate(config, rules)

    @classmethod
    def bulk_import(cls, configs: list):
        _error = False
        _validation = []
        _counter = 0
        for config in configs:
            v = cls.validate_import(config=config)
            if v.failed():
                _error = True
                _validation.append(v.get_messages())
            else:
                _config = cls(**config)
                _config.save()
                _counter += 1
                _validation.append(None)
        return (_counter, _validation) if _error else (_counter, [])
