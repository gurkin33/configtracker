from respect_validation.Rules.AbstractRule import AbstractRule
from sqlalchemy import and_

from api.src.models import NotificationsConfigModel


class NotificationsConfig(AbstractRule):

    def __init__(self, config_id: str = None, user_id: bool = True):
        super().__init__()
        self._user_id = user_id
        self._config_id = config_id

    def validate(self, input_val) -> bool:

        if self._user_id:
            return not bool(NotificationsConfigModel.query.filter(and_(
                NotificationsConfigModel.config_id == self._config_id,
                NotificationsConfigModel.user_id == input_val)).first())

        return not bool(NotificationsConfigModel.query.filter(and_(
            NotificationsConfigModel.config_id == self._config_id,
            NotificationsConfigModel.group_id == input_val)).first())
