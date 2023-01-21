#!/usr/bin/env python

import os
import sys

from configtracker.engine.config import ConfigEngine
from configtracker.mail_service import MailService
from api.db import db
from api.config import GlobalConfig
from configtracker.engine.connectors.connector_manager import ConnectorManager
from mini_app import app
from concurrent.futures import ThreadPoolExecutor
from configtracker import log
from configtracker.engine.git_handler import GitHandler
from configtracker.engine.error_reporter import ErrorReporter
from api.src.models.repository import RepositoryModel
from api.src.models.repo_stats import RepoStatsModel
from api.src.models.config import ConfigModel
from configtracker.models.repo import RepoModel


known_hosts = os.path.expanduser("~/.ssh/known_hosts")
if os.path.exists(known_hosts):
    log.info("Clear know_hosts file")
    open(known_hosts, 'w').close()

log.info("Set all configs in process status")
with app.app_context():
    ConfigModel.set_in_process()

log.info("Get repositories")
repositories = []
with app.app_context():
    for repo in RepositoryModel.query.all():
        repositories.append(RepoModel(**repo.get_config()))

log.info("Error Reporter init")
ErrorReporter.clear()

threads = GlobalConfig.ENGINE_DEFAULT_THREADS
log.info("Run main script")
for repo in repositories:
    log.info(f"Repository {repo.name} in process")
    GitHandler(repo_id=repo.id, name=repo.name, git_username=repo.id, git_email="config_tracker@local")
    with ThreadPoolExecutor(threads, thread_name_prefix="thread_id") as executor:
        for config in repo.configs:
            log.info(f"Config start execute {config.name}")
            executor.submit(config.exec)
    log.info(f"Commit repository {repo.name}")
    repo_stats = GitHandler.commit(repo_id=repo.id)
    log.info(f"Repository {repo.name} in done")
    with app.app_context():
        _repo = RepositoryModel.find_by_id(repo.id)
        _repo.size = repo_stats['size']
        _repo.commits = repo_stats['commits']
        _repo.last_commit = repo_stats['last_commit']
        _stats = []
        for stat in repo_stats['stats']:
            _stats.append(RepoStatsModel(**stat))
        # print(_stats)
        _repo.stats = _stats
        _repo.save()

        _config_ids = []
        for c in os.listdir(f"{GlobalConfig.REPOS_ROOT_PATH}/{repo.id}"):
            if os.path.islink(os.path.join(f"{GlobalConfig.REPOS_ROOT_PATH}/{repo.id}", c)) or c in ['.gitignore', '.git']:
                continue
            _config_ids.append(c)
        if _config_ids:
            ConfigModel.query.filter(ConfigModel.id.in_(_config_ids)).update(dict(exists=True))
            db.session.commit()

log.info('Set configs size')
ConnectorManager.set_config_properties()
log.info('Remove all temp files')
ConnectorManager.remove_all_ssh_keys()
log.info('Send reports')
repos = [(r.id, r.name) for r in repositories]
MailService.send_reports(ConfigEngine.get_notifications(), dict(repos))

log.info('Service exit')
sys.exit(0)
