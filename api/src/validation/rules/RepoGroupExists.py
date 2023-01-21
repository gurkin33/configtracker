from respect_validation.Rules.AbstractRule import AbstractRule

from api.src.models import RepoGroupModel


class RepoGroupExists(AbstractRule):

    def __init__(self, repo_id: str = None):
        super().__init__()
        self._repo_id = repo_id

    def validate(self, input_val) -> bool:
        # print('Current repo id', self._repo_id)
        if not self._repo_id:
            return bool(RepoGroupModel.query.filter(RepoGroupModel.id == input_val).first())

        # print(RepoGroupModel.query.filter(RepoGroupModel.id == _id).filter(RepoGroupModel.repo_id == self._repo_id))
        return bool(RepoGroupModel.query.filter(RepoGroupModel.id == input_val).filter(
            RepoGroupModel.repo_id == self._repo_id).first())
