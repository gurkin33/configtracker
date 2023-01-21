from respect_validation.Rules.AbstractRule import AbstractRule
from sqlalchemy import and_

from api.src.models import NotificationsRepositoryModel


class NotificationsRepo(AbstractRule):

    def __init__(self, repo_id: str = None, user_id: bool = True):
        super().__init__()
        self._user_id = user_id
        self._repo_id = repo_id

    def validate(self, input_val) -> bool:

        if self._user_id:
            return not bool(NotificationsRepositoryModel.query.filter(and_(
                NotificationsRepositoryModel.repo_id == self._repo_id,
                NotificationsRepositoryModel.user_id == input_val)).first())

        return not bool(NotificationsRepositoryModel.query.filter(and_(
            NotificationsRepositoryModel.repo_id == self._repo_id,
            NotificationsRepositoryModel.group_id == input_val)).first())
