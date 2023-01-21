import re

import git
from api.config import GlobalConfig


class ConfigGitParent:
    id: str
    repo_id: str

    def commit_exists(self, commit: str):
        repo = git.Repo(f"{GlobalConfig.REPOS_ROOT_PATH}/{self.repo_id}")
        try:
            repo.git.execute(['git', 'cat-file', 'commit', commit])
        except:
            return False
        return True

    def get_git_diff(self, commit_a: str, commit_b: str, context: int = 1):
        repo = git.Repo(f"{GlobalConfig.REPOS_ROOT_PATH}/{self.repo_id}")

        diff = repo.git.diff(commit_a, commit_b, f"--unified={context}", '--', f"{self.id}")
        return diff

    def get_git_log(self, last_n: int, after: str = "", before: str = ""):
        g = git.Git(f"{GlobalConfig.REPOS_ROOT_PATH}/{self.repo_id}")
        git_log_param = []
        if last_n:
            git_log_param.append(f"-n {last_n}")
        if after:
            git_log_param.append(f'--after="{after}"')
        if before:
            git_log_param.append(f'--before="{before}"')
        # git log --oneline --pretty=format:"%H%x09%ct" --numstat --raw -- CONFIG_ID
        log_info = g.log(*git_log_param, '--oneline', '--pretty=format:%H%x09%ct', '--numstat', '--raw', '--', self.id)
        return self._git_log_parser(log_info)

    @staticmethod
    def _git_log_parser(log: str):
        output = []
        if not log:
            return output
        commits = re.split(r'\n\n', log)
        for commit in commits:
            status = re.search(r'\w$', commit.split("\n")[1].split("\t")[0])
            if status:
                status = status.group(0)
            insertions = str(commit.split("\n")[2].split("\t")[0])
            if insertions.isdigit():
                insertions = int(insertions)
            deletions = str(commit.split("\n")[2].split("\t")[1])
            if deletions.isdigit():
                deletions = int(deletions)
            output.append({
                "commit": commit.split("\n")[0].split("\t")[0],
                "time": int(commit.split("\n")[0].split("\t")[1]),
                "status": status,
                "insertions": insertions,
                "deletions": deletions,
            })
        return output

    def get_data(self, commit: str = None, binary_ignore: bool = True):
        if commit:
            repo = git.Repo(f"{GlobalConfig.REPOS_ROOT_PATH}/{self.repo_id}")
            if repo.git.log(commit, '--oneline', '--diff-filter=D', '--', self.id):
                return ''
            if binary_ignore and self._data_is_binary(repo, commit):
                return None
            res = repo.git.show(f"{commit}:{self.id}")
            return res
        else:
            # detect if file is binary
            # if so return None
            # binary detector from here:
            # https://stackoverflow.com/questions/898669/how-can-i-detect-if-a-file-is-binary-non-text-in-python
            text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})

            def is_binary_string(_bytes):
                return bool(_bytes.translate(None, text_chars))
            if binary_ignore and is_binary_string(open(f"{GlobalConfig.REPOS_ROOT_PATH}/{self.repo_id}/{self.id}", 'rb').read(1024)):
                return None
            with open(f"{GlobalConfig.REPOS_ROOT_PATH}/{self.repo_id}/{self.id}") as f:
                return f.read()

    def _data_is_binary(self, repo, commit: str):
        commit_a = f"{commit}~"
        commit_b = commit
        regex = r"^-\s+-\s+"
        return bool(re.match(regex, repo.git.diff('--numstat', commit_a, commit_b, '--', self.id)))
