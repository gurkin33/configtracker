from respect_validation.Rules.AbstractRule import AbstractRule

from api.src.models import UserGroupModel


class UserGroupExists(AbstractRule):

    def validate(self, input_val) -> bool:
        _id = ''
        if isinstance(input_val, str):
            _id = input_val
        if isinstance(input_val, dict):
            _id = str(input_val.get('id'))
        return bool(UserGroupModel.query.filter(UserGroupModel.id == _id).first())
