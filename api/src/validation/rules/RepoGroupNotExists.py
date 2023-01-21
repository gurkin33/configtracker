from respect_validation.Rules.AbstractRule import AbstractRule

from api.src.models import RepoGroupModel


class RepoGroupNotExists(AbstractRule):

    _repo_id = ''
    _parent_id = ''
    _id = 0

    def __init__(self, repo_id: str = '', obj_id: str = '', parent_id: str = ''):
        super().__init__()
        self._repo_id = str(repo_id)
        self._parent_id = parent_id
        self._id = str(obj_id)

    def validate(self, input_val) -> bool:
        filter_data = dict()
        filter_data['name'] = str(input_val)
        filter_data['repo_id'] = str(self._repo_id)
        filter_data['parent_id'] = self._parent_id if self._parent_id else None
        # print(filter_data, self._id)
        # print(RepoGroupModel.query.filter_by(**filter_data).filter(RepoGroupModel.id != str(self._id)).first())
        # print(RepoGroupModel.query.filter_by(**filter_data).filter(RepoGroupModel.id != str(self._id)))
        # print(RepoGroupModel.query.filter_by(**filter_data).first())
        if not self._id:
            return not RepoGroupModel.query.filter_by(**filter_data).first()
        return not RepoGroupModel.query.filter_by(**filter_data).filter(RepoGroupModel.id != str(self._id)).first()
