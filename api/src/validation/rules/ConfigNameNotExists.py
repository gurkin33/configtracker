from respect_validation.Rules.AbstractRule import AbstractRule
from sqlalchemy import and_

from api.src.models import ConfigModel


class ConfigNameNotExists(AbstractRule):
    _repo_id: str = ''
    _group_id: str = None
    _id: str = ''

    def __init__(self, repo_id: str = None, group_id: str = None, _id: str = ''):
        super().__init__()
        self._repo_id = str(repo_id)
        self._group_id = str(group_id) if group_id else None
        self._id = _id

    def validate(self, input_val) -> bool:
        # print('Current repo id', self._repo_id)
        if not self._repo_id:
            return False
        # print(RepoGroupModel.query.filter(RepoGroupModel.id == _id).filter(RepoGroupModel.repo_id == self._repo_id))
        return not bool(ConfigModel.query.filter(and_(ConfigModel.name == str(input_val),
                                                      ConfigModel.repo_id == self._repo_id,
                                                      ConfigModel.repo_group_id == self._group_id,
                                                      ConfigModel.id != self._id)).count())
