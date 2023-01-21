from respect_validation.Rules.AbstractRule import AbstractRule
from sqlalchemy import and_

from api.src.models import NotificationsRepoGroupModel


class NotificationsRepoGroup(AbstractRule):

    def __init__(self, repo_group_id: str = None, user_id: bool = True):
        super().__init__()
        self._user_id = user_id
        self._repo_group_id = repo_group_id

    def validate(self, input_val) -> bool:

        if self._user_id:
            return not bool(NotificationsRepoGroupModel.query.filter(and_(
                NotificationsRepoGroupModel.repo_group_id == self._repo_group_id,
                NotificationsRepoGroupModel.user_id == input_val)).first())

        return not bool(NotificationsRepoGroupModel.query.filter(and_(
            NotificationsRepoGroupModel.repo_group_id == self._repo_group_id,
            NotificationsRepoGroupModel.group_id == input_val)).first())
