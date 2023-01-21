import filecmp
import os
import re
from glob import glob

from git import Repo, GitCmdObjectDB
from datetime import datetime
from os import path, replace, remove, mkdir, symlink

from api.config import GlobalConfig
from configtracker import log
from configtracker.engine import ConfigFile
from configtracker.models import ConfigModel


class GitHandler:

    REPO_PATH: str = ''

    def __init__(self, repo_id: str, name: str, git_username: str, git_email: str):
        self.REPO_PATH = f"{GlobalConfig.REPOS_ROOT_PATH}/{repo_id}"
        if not path.isdir(self.REPO_PATH):
            log.info(f"Repository {repo_id} ({name}) not found. Init container")
            log.info(f"Create directory {self.REPO_PATH}")
            mkdir(self.REPO_PATH)
            log.info(f"Create symlink for repo {GlobalConfig.REPOS_ROOT_PATH}/{name}")
            symlink(self.REPO_PATH, f"{GlobalConfig.REPOS_ROOT_PATH}/{name}")
            log.info("Create .gitignore")
            with open(f"{self.REPO_PATH}/.gitignore", "w") as f:
                f.write("*.__temp__\n*.lnk")

            log.info("Init git container")
            r = Repo.init(self.REPO_PATH, odbt=GitCmdObjectDB)
            r.config_writer().set_value("user", "name", "config_tracker").release()
            r.config_writer().set_value("user", "email", "config_tracker@local").release()
            r.git.add('--all')
            r.index.commit('First commit')

    @classmethod
    def add(cls, config: ConfigModel, file: ConfigFile):
        file_path = f'{GlobalConfig.REPOS_ROOT_PATH}/{config.repo_id}/{config.id}'
        log.info(f"Add {file_path} to container")
        if path.isfile(file_path):
            log.debug(f"File {file_path} exists. Create temp file")
            file.save(path=file_path + '.__temp__')
            # with open(file_path + '.__temp__', 'w') as f:
            #     f.write(output)
            log.debug(f"Compare current and temp files")
            if not filecmp.cmp(file_path, f'{file_path}.__temp__', shallow=False):
                log.debug(f"Changes found. Save file")
                replace(f'{file_path}.__temp__', file_path)
                config.set_notification()
            else:
                log.debug(f"Changes NOT found. Remove temp file")
                remove(f'{file_path}.__temp__')
        else:
            log.debug(f"File {file_path} not exists. Create one")
            file.save(path=file_path)
            # with open(file_path, 'w') as f:
            #     f.write(output)
        cls._add_config_symlink(config.repo_id, config.id, config.name)

    @classmethod
    def _add_config_symlink(cls, repo_id: str, config_id: str, config_name: str):
        file_path = f'{GlobalConfig.REPOS_ROOT_PATH}/{repo_id}/{config_id}'
        log.debug(f"Add symlink {file_path} to container")
        if path.isfile(file_path):
            log.debug(f"File {file_path} exists. Check symlink")
            links = glob(f'{GlobalConfig.REPOS_ROOT_PATH}/{repo_id}/*-{config_id}.lnk')
            if len(links):
                log.debug(f"Symlink found delete it")
                for link in links:
                    remove(link)
            else:
                log.debug(f"Symlink not found")
            log.debug(f"Create symlink {GlobalConfig.REPOS_ROOT_PATH}/{repo_id}/{config_name}-{config_id}.lnk")
            symlink(file_path, f'{GlobalConfig.REPOS_ROOT_PATH}/{repo_id}/{config_name}-{config_id}.lnk')

    @classmethod
    def commit(cls, repo_id: str):
        repo_path = f"{GlobalConfig.REPOS_ROOT_PATH}/{repo_id}"
        r = Repo(repo_path)
        r.git.add(all=True)
        if len(r.index.diff("HEAD")):
            log.debug(f"git commit change")
            r.index.commit(f'"{datetime.now()}"')
        else:
            log.debug(f"git changes not found")
        stats = {
            "size": int(cls._get_dir_size(repo_path)),
            "commits": int(r.git.rev_list('--count', 'HEAD')),
            "last_commit": datetime.fromtimestamp(
                int(r.git.log('-1', '--format=%ct'))).replace(microsecond=0).isoformat(),
            "stats": cls._parse_git_log(r.git.log('--oneline', '-n 8', '--pretty=format:%H%x09%ct', '--stat'))
        }
        log.debug(f"Repo size: {stats['size']}")
        log.debug(f"Repo commits: {stats['commits']}")
        log.debug(f"Repo last commit: {stats['last_commit']}")
        # commits = cls._parse_git_log(r.git.log('--oneline', '-n 8', '--pretty=format:%H%x09%ct', '--stat'))
        log.debug(f"Repo last 8 commits: {stats['stats']}")

        return stats

    @classmethod
    def _get_dir_size(cls, repo_path: str):
        total = 0
        with os.scandir(repo_path) as it:
            for entry in it:
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += cls._get_dir_size(entry.path)
        return total

    @classmethod
    def _parse_git_log(cls, git_commits: str):
        commits = []
        for commit in git_commits.split('\n\n'):
            _commit = commit.split('\n')
            commits.append({
                "date": datetime.fromtimestamp(int(_commit[0].split('\t')[1])).replace(microsecond=0).isoformat(),
                **cls._git_stat_parser(_commit[-1])
            })
        return commits

    @staticmethod
    def _git_stat_parser(stats: str):
        _stats = {
            "files_changed": 0,
            "insertions": 0,
            "deletions": 0,
        }
        for stat in stats.split(', '):
            if re.match(r'.*file.*', stat):
                _stats['files_changed'] = int(stat.strip().split(' ')[0])
                continue
            if re.match(r'.*insertion.*', stat):
                _stats['insertions'] = int(stat.strip().split(' ')[0])
                continue
            if re.match(r'.*deletion.*', stat):
                _stats['deletions'] = int(stat.strip().split(' ')[0])
                continue
        return _stats
